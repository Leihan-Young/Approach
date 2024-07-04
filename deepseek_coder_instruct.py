import json
import os
import torch
import javalang
import re
import copy
import traceback
import subprocess as sp
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import infer_auto_device_map, dispatch_model
from accelerate.utils import get_balanced_memory

cov_cli_path = "/data/zhiquanyang/Co-evolution/Benchmark"
repos_path = "/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors"
model_path = "/nasdata/Model/deepseek-coder-6.7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)

conversation_length = 3

CONTEXT = "$CONTEXT$"
FOCAL_SRC = "$FOCAL_SRC$"
FOCAL_TGT = "$FOCAL_TGT$"
FOCAL_TGT_COV = "$FOCAL_TGT_COV$"
TEST_SRC = "$TEST_SRC$"
TEST_FIX = "$TEST_FIX$"
TEST_PREFIX = "$TEST_PREFIX$"
TEST_SIGNATURE = "$TEST_SIGNATURE$"
TEST_INCOMPLETE = "$TEST_INCOMPLETE$"
ENHANCE_RESPONSE = "$ENHANCE_RESPONSE$"
EOT = "<|EOT|>"

identify_prompt = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
I will provide you the old version of production code and the old version of test code.
Since the production code has been changed, the test code may needs to be updated.
You are going to check whether the test code needs to be updated.
Answer 'Yes' or 'No'.
### Response:
Sure, I will check whether the test code needs to be updated.
{EOT}
### Instruction:
```java
// The old version of production code.
{FOCAL_SRC}
// The corresponding test code.
{TEST_SRC}
```
The production code has changed.
```java
// The updated version of procution code.
{FOCAL_TGT}
// The corresponding test code.
{TEST_SRC}
```
Should the corresponding test code be updated with the production code changes?
### Response:
"""

fix_prompt = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
You are going to complete the incomplete code blocks with following template.
@Test
public void test(){'{'}
    assertTrue(boolTrue);
{'}'}
```
### Response:
Sure, I will complete the following incomplete code block with the template.
@Test
public void test(){'{'}
    assertTrue(boolTrue);
{'}'}
```
{EOT}
### Instruction:
The old version of production code and test code.
```java
// The old version of the production code
{FOCAL_SRC}
// The old version of the test code that tests the old version of the production code
{TEST_SRC}
```
Since the production code has changed, the old version of test code needs to be maintained.
Notice that not all methods invoked in test code is changed.
```java
// The updated version of the production code
{FOCAL_TGT}
// Some context in the production code
{CONTEXT}
// The updated version of the test code that co-evolves with the production code
### Response:
{TEST_SIGNATURE}
"""

enhance_prompt = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
The existing test code can not cover all the production code.
I will provide you the production code with comments showing the coverage and existing test code.
You should consider how to cover the uncovered lines and branches.
You can only write more statements in the test code provided.
Another test case is not allowed.
### Response:
Sure.
{EOT}
### Instruction:
The production code.
```java
{FOCAL_TGT_COV}
```
The corresponding test code
```java
{TEST_FIX}
```
Let's think step by step before writing test code.
### Response:
"""

enhance_generate_prompt = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
The existing test code can not cover all the production code.
I will provide you the production code with comments showing the coverage and existing test code.
You should consider how to cover the uncovered lines and branches.
You can only write more statements in the test code provided.
Another test case is not allowed.
### Response:
Sure.
{EOT}
### Instruction:
The production code.
```java
{FOCAL_TGT_COV}
```
The corresponding test code
```java
{TEST_FIX}
```
Let's think step by step before writing test code.
### Response:
{ENHANCE_RESPONSE}
{EOT}
### Instruction:
Now let's write a test case to cover the uncovered lines and branches.
### Response:
{TEST_INCOMPLETE}
"""

enhance_prompt_backup = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
The existing test code can not cover all the production code.
I will provide you the production code with comments showing the coverage.
You should write more test code to cover the uncovered lines and branches.
### Response:
Sure, I will write test code to cover the uncovered lines and branches.
{EOT}
### Instruction:
The production code.
```java
{FOCAL_TGT_COV}
```
The corresponding test code
```java
{TEST_FIX}
```
### Response:
{TEST_INCOMPLETE}
"""


def get_context_with_specified_body(work_dir, prod_path, require_body_list):
    result_context = ""
    files = []
    exclude_methods = []
    for p in prod_path:
        file = p.split('#')[0]
        if file not in files:
            files.append(file)
        method = p.split('#')[1]
        if method not in exclude_methods:
            exclude_methods.append(method)
    for file in files:
        with open(os.path.join(work_dir, file), 'r') as f:
            java_code = f.read()
        java_code_lines = [l+'\n' for l in java_code.split("\n", )]
        root = javalang.parse.parse(java_code)
        class_body = root.children[2][0].body
        fields = []
        constructors = []
        methods = []
        for node in class_body:
            if isinstance(node, javalang.tree.FieldDeclaration):
                fields.append(node)
            elif isinstance(node, javalang.tree.ConstructorDeclaration):
                constructors.append(node)
            elif isinstance(node, javalang.tree.MethodDeclaration):
                methods.append(node)

        context = ""
        for node in fields:
            ind = node.position.line - 1
            field_context = ""
            while ind < len(java_code_lines):
                line = java_code_lines[ind]
                # remove comments
                if line.find('//') != -1:
                    line = line[:line.find('//')] + '\n'
                field_context += line
                if field_context.rstrip().endswith(';'):
                    break
            context += field_context
        for node in constructors:
            ind = node.position.line - 1
            constructor_context = get_java_code_method(java_code_lines, ind)
            context += constructor_context
        for node in methods:
            ind = node.position.line - 1
            try:
                method_context = get_java_code_method(java_code_lines, ind, node.name in require_body_list)
            except:
                method_context = get_java_code_method(java_code_lines, ind)
            context += method_context
        result_context += context
    # remove leading spaces
    result_context = result_context.rstrip().split('\n')
    leading_spaces = len(result_context[0])-len(result_context[0].lstrip())
    for line in result_context:
        leading = len(line) - len(line.lstrip())
        if leading < leading_spaces:
            leading_spaces = leading
    result_context = '\n'.join([l[leading_spaces:] for l in result_context])
    return result_context

def get_java_code_method(java_code, start, include_body=False):
    if include_body:
        # 找方法结尾
        end = start
        comment = False
        count = None
        end = end - 1
        while end + 1 < len(java_code) or count == None:
            end = end + 1
            if comment and java_code[end].find('*/') != -1:
                comment = False
                continue
            if java_code[end].find('/*') != -1 and java_code[end].find('*/') == -1 and java_code[end][:java_code[end].find('/*')].find('"') == -1 and java_code[end][:java_code[end].find('/*')].find('}') == -1:
                comment = True
                continue
            if count_symbol(java_code[end], ';') != 0 and count == None:
                break
            left_count = count_symbol(java_code[end], '{')
            right_count = count_symbol(java_code[end], '}')
            diff = left_count - right_count
            if count == None and diff != 0:
                count = diff
            elif count != None:
                count = count + diff
            if count != None and count <= 0:
                break
        if java_code[end].find('/*') != -1 and java_code[end][:java_code[end].find('/*')].find('"') == -1 and java_code[end][:java_code[end].find('/*')].find('}') == -1:
            java_code[end] = java_code[end][:java_code[end].find('}') + 1]
        end = end + 1
        if end >= len(java_code):
            raise Exception("Error:Unexpected error in getJavaCodeMethod()")
        # 回退末尾不需要的内容
        if java_code[end].find('public ') != -1 or java_code[end].find('private ') != -1:
            end = end - 1
            while end > start and java_code[end].find('@') != -1:
                end = end - 1
            if java_code[end].find('*/') != -1:
                while end > start and java_code[end].find('/*') == -1:
                    end = end - 1
        return ''.join(java_code[start:end])
    
    else:
        res_line = java_code[start]
        if res_line.find('//') != -1:
            res_line = res_line[:res_line.find('//')] + '\n'
        while count_symbol(res_line, '{') == 0:
            i = start + 1
            res_line += java_code[i]
            if res_line.find('//') != -1:
                res_line = res_line[:res_line.find('//')] + '\n'
        res_line = res_line[:res_line.find('{')].rstrip() + ';\n'
        return res_line

# return True if success
def gen_evosuite_tests(work_dir, output_dir):
    command = f"python cli.py evosuite -w {work_dir} -o {os.path.abspath(output_dir)} -c"
    run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
    stdout = run.stdout.decode()
    if "Succeed to generate Evosuite tests" in stdout:
        return True
    return False

def extract_related_methods(test_file_path, target_methods):
    related_prod_methods = []
    related_test_methods = []
    test_methods = []
    for path, dirs, files in os.walk(test_file_path):
        for file in files:
            if file.endswith("ESTest.java"):
                test_methods += extract_all_test_methods_in_file(os.path.join(path, file))
    
    test_methods = ["public void test" + l[l.find('()'):] for l in test_methods]

    for test_method in test_methods:
        for target_method in target_methods:
            if target_method in test_method:
                root = javalang.parse.parse(f"public class TempClass {{{test_method}}}")
                qualifiers = set()
                for path, node in root.filter(javalang.tree.MethodInvocation):
                    if node.member == target_method:
                        qualifiers.add(node.qualifier)
                if len(qualifiers) == 0:
                    continue
                if test_method not in related_test_methods:
                    related_test_methods.append(test_method)
                for path, node in root.filter(javalang.tree.MethodInvocation):
                    if node.qualifier in qualifiers and node.member != target_method and node.member not in related_prod_methods:
                        related_prod_methods.append(node.member)
    return related_prod_methods, related_test_methods


def extract_all_test_methods_in_file(test_file_path):
    methods = []
    with open(test_file_path, 'r') as file:
        test_code = file.readlines()
    in_method = False
    method_start_flag = 0
    method_end = "  }"
    for i, line in enumerate(test_code):
        if not in_method and line.lstrip().startswith("@Test"):
            in_method = True
            method_start_flag = i+1
        if in_method and line.startswith(method_end):
            in_method = False
            methods.append(''.join(test_code[method_start_flag:i+1]))
    return methods

def extract_test_signature(test):
    ind = test.find('{')
    signature = test[:ind]
    if test[ind+1:].lstrip().startswith('\n'):
        suf = test[ind+1:]
        signature += suf[:suf.find('\n')]
    return signature

def extract_test_incomplete(test):
    ind = test.rfind('}')
    return test[:ind]

def check_focal_equal(src_lines, focal_cov, idx):
    for i in range(min(len(src_lines), 10)):
        if src_lines[i] not in focal_cov[idx+i]:
            return False
    return True
    
def full_cov_count(cov):
    cov = '\n'.join(cov)
    return cov.count('// Covered')

def evaluate_cov(tests, pid, tid, focal_path, focal_code_):
    focal_code = copy.deepcopy(focal_code_)
    cov_res = []
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')
    if not os.path.exists('./output'):
        os.makedirs('./output')
    # command = f"python cli.py clean -w {os.path.join(repos_path, pid, f'{tid}t')}"
    # run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
    # print(run.stdout.decode())
    for test in tests:
        with open('./tmp/input.java', 'w', encoding='utf-8') as f:
            f.write(test)
        command = f"python cli.py coverage -w {os.path.join(repos_path, pid, f'{tid}t')} -o {os.path.abspath('./output')} -i {os.path.abspath('./tmp/input.java')}"
        run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
        print(run.stdout.decode())
        if "BUILD FAILURE" in run.stdout.decode() or "Fail to parse" in run.stdout.decode():
            cov_res.append(None)
            continue
        cov = []
        for idx1, path in enumerate(focal_path):
            cov_html_file = os.path.join('./output', f'{path[path.rfind("/")+1:].split("#")[0]}.html')
            with open(cov_html_file, 'r', encoding='utf-8') as f:
                cov_html_lines = f.readlines()
            src_lines = focal_code[idx1].split('\n')
            for idx2, line in enumerate(cov_html_lines):
                if len(cov_html_lines) > idx2+len(src_lines)-1 and check_focal_equal(src_lines, cov_html_lines, idx2):
                    cov.append(cov_html_lines[idx2:idx2+len(src_lines)])
                    break
        cov_res.append(cov)
        output_files = os.listdir('./output')
        for output_file in output_files:
            os.remove(os.path.join('./output', output_file))
    
    for idx, code in enumerate(focal_code):
        lines = code.split('\n')
        lines = [f"{l}\n" for l in lines]
        focal_code[idx] = lines

    prefix_pattern = r'<span class=".*".*">'
    for tid, cov in enumerate(cov_res):
        if cov is None:
            continue
        for idx1, cov_lines in enumerate(cov):
            if cov_lines is None:
                continue
            for idx2, line in enumerate(cov_lines):
                span = re.match(prefix_pattern, line)
                if span is None:
                    cov_res[tid][idx1][idx2] = focal_code[idx1][idx2]
                    continue
                span = span.group(0)
                cover_class = span.split(' ')[1].split('=')[-1].replace('"', '')
                if cover_class.startswith('nc'):
                    text = "Not Covered"
                elif cover_class.startswith('fc'):
                    text = "Covered"
                elif cover_class.startswith('pc'):
                    text = "Partially Covered"
                else:
                    print("Error class")
                    print(cover_class)
                    cov_res[tid][idx1][idx2] = focal_code[idx1][idx2]
                    continue
                cov_res[tid][idx1][idx2] = focal_code[idx1][idx2].replace('\n', '') + f' // {text}\n'
        
    for cov in cov_res:
        if cov is None:
            continue
        for idx, c in enumerate(cov):
            cov[idx] = align_code(''.join(c))

    return cov_res
    
def checkout(pid, tid, repo_path, commit):
    sp.run('git reset --hard HEAD',
        cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)
    sp.run('git clean -df',
        cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)
    sp.run(f'git checkout {commit}',
        stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path, shell=True)
    with open(f"{repo_path}/.pidtid.config", "w") as f:
        f.write("#File automatically generated\n")
        f.write(f"pid={pid}\n")
        f.write(f"tid={tid}")
        f.close()

def count_symbol(line, symbol):
    count = 0
    string_flag = False
    char_flag = False
    for i in range(len(line)):
        if line[i] == '/' and i + 1 < len(line) and line[i+1] == '/' and not string_flag and not char_flag:
            break
        if line[i] == '"' and (i == 0 or line[i - 1] != '\\'):
            string_flag = not string_flag
        if line[i] == '\'' and (i == 0 or line[i - 1] != '\\') and not string_flag:
            char_flag = not char_flag
        if string_flag or char_flag:
            continue
        if line[i] == symbol:
            count = count + 1
    return count

def extract_test_method(s):
    end = 1
    comment = False
    lines = s.split('\n')
    lines = [l.rstrip() for l in lines]
    count = None
    end = end - 1
    while end + 1 < len(lines):
        end = end + 1
        if comment and lines[end].find('*/') != -1:
            comment = False
            continue
        if lines[end].find('/*') != -1 and lines[end].find('*/') == -1 and lines[end][:lines[end].find('/*')].find('"') == -1 and lines[end][:lines[end].find('/*')].find('}') == -1:
            comment = True
            continue
        left_count = count_symbol(lines[end], '{')
        right_count = count_symbol(lines[end], '}')
        diff = left_count - right_count
        if count == None and diff != 0:
            count = diff
        elif count != None:
            count = count + diff
        if count != None and count <= 0:
            break
    if lines[end].find('/*') != -1 and lines[end][:lines[end].find('/*')].find('"') == -1 and lines[end][:lines[end].find('/*')].find('}') == -1:
        lines[end] = lines[end][:lines[end].find('}') + 1]
    if lines[end].endswith('\n'):
        lines[end] = lines[end][:-1]
    if count > 0:
        return None
    lines[end] += '\n'
    end = end + 1
    if end < len(lines):
        lines = lines[:end]
    if lines[-1].lstrip().startswith('}'):
        lines[0] = lines[-1][:lines[-1].find('}')] + lines[0]
    test = align_code("\n".join(lines))
    return test

def fix_test(context, focal_src, focal_tgt, test_src):
    test_signature = extract_test_signature(test_src)
    input_text = fix_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src).replace(TEST_SIGNATURE, test_signature).replace(CONTEXT, context)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    test_fix = []
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=10, eos_token_id=tokenizer.eos_token_id)
    for output in outputs:
        text_gen = test_signature + '\n' + tokenizer.decode(output, skip_special_tokens=True)[len(input_text) - len(EOT):]
        test = extract_test_method(text_gen)
        if test is not None:
            test_fix.append(test)
    return test_fix

def enhance_test(focal_tgt_cov, test_fix):
    test_enhance = []
    focal_tgt_cov = '\n'.join(focal_tgt_cov)
    if not ("Not Covered" in focal_tgt_cov or "Partially Covered" in focal_tgt_cov):
        print("all_covered")
        test_enhance = test_fix
        return "all_covered"
    input_text = enhance_prompt.replace(FOCAL_TGT_COV, focal_tgt_cov).replace(TEST_FIX, test_fix)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
    cot_response = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text) - len(EOT):]
    print(cot_response)

    test_incomplete = extract_test_incomplete(test_fix)
    input_text = enhance_generate_prompt.replace(FOCAL_TGT_COV, focal_tgt_cov).replace(TEST_FIX, test_fix).replace(ENHANCE_RESPONSE, cot_response).replace(TEST_INCOMPLETE, test_incomplete)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=5, eos_token_id=tokenizer.eos_token_id)
    for output in outputs:
        text_gen = test_incomplete + tokenizer.decode(output, skip_special_tokens=True)[len(input_text) - 2 * len(EOT):]
        test = extract_test_method(text_gen)
        if test is not None:
            test_enhance.append(test)
    return test_enhance

def identify_obsolete(focal_src, focal_tgt, test_src):
    input_text = identify_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256, do_sample=False, top_k=50, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
    text_gen = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text) - len(EOT):]
    if text_gen.startswith('No'):
        return False
    return True

def align_code(code):
    code_lines = code.split('\n')
    move = len(code_lines[0]) - len(code_lines[0].lstrip())
    for i in range(len(code_lines)):
        if len(code_lines[i].lstrip().rstrip()) == 0:
            continue
        if move > len(code_lines[i]) - len(code_lines[i].lstrip()):
            move = len(code_lines[i]) - len(code_lines[i].lstrip())
    aligned_code = [l[move:] if len(l.lstrip().rstrip()) != 0 else l for l in code_lines]
    return '\n'.join(aligned_code)

def invoke_model(focal_src, focal_tgt, test_src):
    focal_src = '\n'.join([align_code(x) for x in focal_src])
    focal_tgt = '\n'.join([align_code(x) for x in focal_tgt])
    test_src = align_code(test_src)
    test_fix = fix_test(focal_src, focal_tgt, test_src)
    checked_test_fix = []
    for test in test_fix:
        try:
            javalang.parse.parse("public class Test {" + test + "}")
            checked_test_fix.append(test)
        except Exception as e:
            continue
    if len(checked_test_fix) == 0:
        checked_test_fix.append('// Fail to generate test fix\n' + test_src)
    return checked_test_fix, None

def rank_by_cov(tests, focal_cov):
    count = []
    for idx, focal in enumerate(focal_cov):
        count.append((idx, focal.count('// Covered')))
    count.sort(reverse=True, key=lambda t: t[1])
    tests_res = []
    focal_cov_res = []
    for idx, _ in count:
        tests_res.append(tests[idx])
        focal_cov_res.append(focal_cov[idx])
    return tests_res, focal_cov_res


def read_json(json_file):
    if not os.path.isfile(json_file):
        return None
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(output_file, obj):
    output_folder = os.sep.join(output_file.split(os.sep)[:-1])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)

if __name__ == "__main__":
    # target_methods = [p.split('#')[1] for p in ["client/src/main/java/com/alibaba/nacos/client/naming/remote/gprc/redo/NamingGrpcRedoService.java#instanceDeregister"]]
    # related_prod, related_tests = extract_related_methods("evosuite_output", target_methods)
    # context = get_context_with_specified_body(os.path.join(repos_path, 'nacos', '1t'), ["client/src/main/java/com/alibaba/nacos/client/naming/remote/gprc/redo/NamingGrpcRedoService.java#instanceDeregister"], related_prod)
    data_path = '/data/zhiquanyang/Co-evolution/Benchmark/verified'
    output_dir = './data'
    files = [name for name in os.listdir(data_path)
                if name.endswith('.json')]
    for idx, file in enumerate(files):
        if os.path.exists(os.path.join(output_dir, file)):
            continue
        print(file)
        pid = file.split('_')[-1].replace('.json', '')
        sample_dict = read_json(os.path.join(data_path, file))
        for key, value in tqdm(sample_dict.items()):
            test_id = value['test_id']
            commit_tgt = value['commit_tgt']
            focal_path_src = value['focal_path_src']
            focal_src = value['focal_src']
            focal_tgt = value['focal_tgt']
            test_src = value['test_src_code']
            focal_src_aligned = '\n'.join([align_code(x) for x in focal_src])
            focal_tgt_aligned = '\n'.join([align_code(x) for x in focal_tgt])
            test_src_aligned = align_code(test_src)
            work_dir = f'/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors/{pid}/{test_id}t'

            try:
                print(f"{pid}:{test_id}")
                identified = identify_obsolete(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
                value['identify_result_deepseek-coder'] = identified
                print(f"Identify Result={identified}")
                if identified:
                    evosuite_output_path = f"./evosuite_output/{pid}/{test_id}"
                    evosuite_gen_success = gen_evosuite_tests(os.path.join(repos_path, pid, f'{test_id}t'), evosuite_output_path)
                    if evosuite_gen_success:
                        target_methods = [p.split('#')[1] for p in focal_path_src]
                        related_prod, related_tests = extract_related_methods(evosuite_output_path, target_methods)
                        context = get_context_with_specified_body(work_dir, focal_path_src, related_prod)
                    else:
                        context = get_context_with_specified_body(work_dir, focal_path_src, [])
                    test_fix = fix_test(context, focal_src_aligned, focal_tgt_aligned, test_src_aligned)
                    checkout(pid, f'{test_id}t', work_dir, commit_tgt)
                    focal_tgt_cov = evaluate_cov(test_fix, pid, test_id, focal_path_src, focal_tgt)
                    tmp_test_fix = []
                    tmp_focal_tgt_cov = []
                    for idx, focal_tgt_cov_item in enumerate(focal_tgt_cov):
                        if focal_tgt_cov_item is None:
                            continue
                        tmp_test_fix.append(test_fix[idx])
                        tmp_focal_tgt_cov.append(focal_tgt_cov_item)
                    test_fix = tmp_test_fix
                    focal_tgt_cov = tmp_focal_tgt_cov
                    print(f"len(test_fix)={len(test_fix)}")
                    if len(test_fix) == 0:
                        test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
                        # test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                    # else:
                    #     test_fix, focal_tgt_cov = rank_by_cov(test_fix, focal_tgt_cov)
                    #     tmp_focal_tgt_covs = focal_tgt_cov
                    #     tmp_tests = test_fix
                    #     for i in range(conversation_length):
                    #         test_enhance = enhance_test(tmp_focal_tgt_covs[0], tmp_tests[0])
                    #         if test_enhance == "all_covered":
                    #             break
                    #         focal_tgt_cov_enhance = evaluate_cov(test_enhance, pid, test_id, focal_path_src, focal_tgt)
                    #         tmp_test_enhance = []
                    #         tmp_focal_tgt_cov_enhance = []
                    #         for idx, focal_tgt_cov_enhance_item in enumerate(focal_tgt_cov_enhance):
                    #             if focal_tgt_cov_enhance_item is None:
                    #                 continue
                    #             tmp_test_enhance.append(test_enhance[idx])
                    #             tmp_focal_tgt_cov_enhance.append(focal_tgt_cov_enhance_item)
                    #         test_enhance = tmp_test_enhance
                    #         focal_tgt_cov_enhance = tmp_focal_tgt_cov_enhance
                    #         if len(test_enhance) == 0:
                    #             continue
                    #         test_enhance, focal_tgt_cov_enhance = rank_by_cov(test_enhance, focal_tgt_cov_enhance)
                    #         print(f"generate_cov_count={full_cov_count(focal_tgt_cov_enhance[0])}")
                    #         print(f"current_cov_count={full_cov_count(tmp_focal_tgt_covs[0])}\n")
                    #         if full_cov_count(focal_tgt_cov_enhance[0]) > full_cov_count(tmp_focal_tgt_covs[0]):
                    #             tmp_tests = test_enhance
                    #             tmp_focal_tgt_covs = focal_tgt_cov_enhance
                    #     test_enhance = tmp_tests
                    #     focal_tgt_cov_enhance = tmp_focal_tgt_covs
                    #     print(f"len(test_enhance)={len(test_enhance)}")
                    #     if len(test_enhance) == 0:
                    #         test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                    value['test_fix_deepseek-coder'] = test_fix
                    # value['test_enhance_deepseek-coder'] = test_enhance
            except Exception as e:
                traceback.print_exc()
                test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
                # test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                value['test_fix_deepseek-coder'] = test_fix
                # value['test_enhance_deepseek-coder'] = test_enhance
                value['exception_while_gen_deepseek-coder'] = repr(e)

        write_json(os.path.join(output_dir, file), sample_dict)


    # pid = "nacos"
    # test_id = '9'
    # commit_tgt = "5994e3739461db0d6052f6e816f309e59c0d0c4b"
    # focal_path_src = ["client/src/main/java/com/alibaba/nacos/client/config/filter/impl/ConfigEncryptionFilter.java#doFilter"]
    # focal_src = ["    @Override\n    public void doFilter(IConfigRequest request, IConfigResponse response, IConfigFilterChain filterChain)\n            throws NacosException {\n        if (Objects.nonNull(request) && request instanceof ConfigRequest && Objects.isNull(response)) {\n            \n            // Publish configuration, encrypt\n            ConfigRequest configRequest = (ConfigRequest) request;\n            String dataId = configRequest.getDataId();\n            String content = configRequest.getContent();\n            \n            Pair<String, String> pair = EncryptionHandler.encryptHandler(dataId, content);\n            String secretKey = pair.getFirst();\n            String encryptContent = pair.getSecond();\n            \n            ((ConfigRequest) request).setContent(encryptContent);\n            ((ConfigRequest) request).setEncryptedDataKey(secretKey);\n        }\n        if (Objects.nonNull(response) && response instanceof ConfigResponse && Objects.isNull(request)) {\n            \n            // Get configuration, decrypt\n            ConfigResponse configResponse = (ConfigResponse) response;\n            \n            String dataId = configResponse.getDataId();\n            String encryptedDataKey = configResponse.getEncryptedDataKey();\n            String content = configResponse.getContent();\n            \n            Pair<String, String> pair = EncryptionHandler.decryptHandler(dataId, encryptedDataKey, content);\n            String decryptContent = pair.getSecond();\n            ((ConfigResponse) response).setContent(decryptContent);\n        }\n        filterChain.doFilter(request, response);\n    }\n"]
    # focal_tgt = ["    @Override\n    public void doFilter(IConfigRequest request, IConfigResponse response, IConfigFilterChain filterChain)\n            throws NacosException {\n        if (Objects.nonNull(request) && request instanceof ConfigRequest && Objects.isNull(response)) {\n            \n            // Publish configuration, encrypt\n            ConfigRequest configRequest = (ConfigRequest) request;\n            String dataId = configRequest.getDataId();\n            String content = configRequest.getContent();\n            \n            Pair<String, String> pair = EncryptionHandler.encryptHandler(dataId, content);\n            String secretKey = pair.getFirst();\n            String encryptContent = pair.getSecond();\n            if (!StringUtils.isBlank(encryptContent) && !encryptContent.equals(content)) {\n                ((ConfigRequest) request).setContent(encryptContent);\n            }\n            if (!StringUtils.isBlank(secretKey) && !secretKey.equals(((ConfigRequest) request).getEncryptedDataKey())) {\n                ((ConfigRequest) request).setEncryptedDataKey(secretKey);\n            } else if (StringUtils.isBlank(((ConfigRequest) request).getEncryptedDataKey()) && StringUtils.isBlank(secretKey)) {\n                ((ConfigRequest) request).setEncryptedDataKey(\"\");\n            }\n        }\n        if (Objects.nonNull(response) && response instanceof ConfigResponse && Objects.isNull(request)) {\n            \n            // Get configuration, decrypt\n            ConfigResponse configResponse = (ConfigResponse) response;\n            \n            String dataId = configResponse.getDataId();\n            String encryptedDataKey = configResponse.getEncryptedDataKey();\n            String content = configResponse.getContent();\n            \n            Pair<String, String> pair = EncryptionHandler.decryptHandler(dataId, encryptedDataKey, content);\n            String secretKey = pair.getFirst();\n            String decryptContent = pair.getSecond();\n            if (!StringUtils.isBlank(decryptContent) && !decryptContent.equals(content)) {\n                ((ConfigResponse) response).setContent(decryptContent);\n            }\n            if (!StringUtils.isBlank(secretKey) && !secretKey.equals(((ConfigResponse) response).getEncryptedDataKey())) {\n                ((ConfigResponse) response).setEncryptedDataKey(secretKey);\n            } else if (StringUtils.isBlank(((ConfigResponse) response).getEncryptedDataKey()) && StringUtils.isBlank(secretKey)) {\n                ((ConfigResponse) response).setEncryptedDataKey(\"\");\n            }\n        }\n        filterChain.doFilter(request, response);\n    }\n"]
    # test_src = "    @Test\n    public void testDoFilter() throws NacosException {\n        configEncryptionFilter.doFilter(configRequest, null, iConfigFilterChain);\n        \n        Mockito.verify(configRequest).getDataId();\n        Mockito.verify(configRequest).getContent();\n        \n        configEncryptionFilter.doFilter(null, configResponse, iConfigFilterChain);\n        \n        Mockito.verify(configResponse).getDataId();\n        Mockito.verify(configResponse).getContent();\n        Mockito.verify(configResponse).getEncryptedDataKey();\n    }\n"
    # focal_src_aligned = '\n'.join([align_code(x) for x in focal_src])
    # focal_tgt_aligned = '\n'.join([align_code(x) for x in focal_tgt])
    # test_src_aligned = align_code(test_src)
    # work_dir = f'/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors/{pid}/{test_id}t'

    # try:
    #     print(f"{pid}:{test_id}")
    #     identified = identify_obsolete(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
    #     if identified:
    #         test_fix = fix_test(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
    #         checkout(pid, f'{test_id}t', work_dir, commit_tgt)
    #         focal_tgt_cov = evaluate_cov(test_fix, pid, test_id, focal_path_src, focal_tgt)
    #         tmp_test_fix = []
    #         tmp_focal_tgt_cov = []
    #         for idx, focal_tgt_cov_item in enumerate(focal_tgt_cov):
    #             if focal_tgt_cov_item is None:
    #                 continue
    #             tmp_test_fix.append(test_fix[idx])
    #             tmp_focal_tgt_cov.append(focal_tgt_cov_item)
    #         test_fix = tmp_test_fix
    #         focal_tgt_cov = tmp_focal_tgt_cov
    #         print(f"len(test_fix)={len(test_fix)}")
    #         if len(test_fix) == 0:
    #             test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
    #             test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
    #         else:
    #             test_fix, _ = rank_by_cov(test_fix, focal_tgt_cov)
    #             tmp_focal_tgt_covs = focal_tgt_cov
    #             tmp_tests = test_fix
    #             for i in range(conversation_length):
    #                 test_enhance = enhance_test(tmp_focal_tgt_covs[0], tmp_tests[0])
    #                 focal_tgt_cov_enhance = evaluate_cov(test_enhance, pid, test_id, focal_path_src, focal_tgt)
    #                 tmp_test_enhance = []
    #                 tmp_focal_tgt_cov_enhance = []
    #                 for idx, focal_tgt_cov_enhance_item in enumerate(focal_tgt_cov_enhance):
    #                     if focal_tgt_cov_enhance_item is None:
    #                         continue
    #                     tmp_test_enhance.append(test_enhance[idx])
    #                     tmp_focal_tgt_cov_enhance.append(focal_tgt_cov_enhance_item)
    #                 test_enhance = tmp_test_enhance
    #                 focal_tgt_cov_enhance = tmp_focal_tgt_cov_enhance
    #                 if len(test_enhance) == 0:
    #                     continue
    #                 test_enhance = rank_by_cov(test_enhance, focal_tgt_cov_enhance)
    #                 if full_cov_count(focal_tgt_cov_enhance[0]) > full_cov_count(tmp_focal_tgt_covs[0]):
    #                     tmp_tests = test_enhance
    #                     tmp_focal_tgt_covs = focal_tgt_cov_enhance
    #                     print("""===============
    #                           =================
    #                           ===================
    #                           =================
    #                           ============""")
    #             test_enhance = tmp_tests
    #             print(test_enhance)
    # except Exception as e:
    #     traceback.print_exc()
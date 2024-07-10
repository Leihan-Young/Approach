import os
import torch
import javalang
import re
import copy
import traceback
import subprocess as sp
import utils
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
CALL_CODES = "$CALL_CODES$"
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
// Some context in the production code
{CONTEXT}
// The updated version of the production code
{FOCAL_TGT}
// The updated version of the test code that co-evolves with the production code
### Response:
{TEST_SIGNATURE}
"""

fix_prompt_with_call_codes = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
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
// Some context in the production code
{CONTEXT}
// The updated version of the production code
{FOCAL_TGT}
// A call to the updated code in productin code
{CALL_CODES}
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

# return True if success
def gen_evosuite_tests(work_dir, output_dir):
    return False
    command = f"python cli.py evosuite -w {work_dir} -o {os.path.abspath(output_dir)} -c"
    run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
    stdout = run.stdout.decode()
    if "Succeed to generate Evosuite tests" in stdout:
        return True
    return False

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
                if len(cov_html_lines) > idx2+len(src_lines)-1 and utils.check_focal_equal(src_lines, cov_html_lines, idx2):
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
            cov[idx] = utils.align_code(''.join(c))

    return cov_res

def fix_test(context, call_code_context, focal_src, focal_tgt, test_src):
    test_signature = utils.extract_test_signature(test_src)
    if call_code_context != "":
        input_text = fix_prompt_with_call_codes.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src).replace(TEST_SIGNATURE, test_signature).replace(CONTEXT, context).replace(CALL_CODES, call_code_context)
    else:
        input_text = fix_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src).replace(TEST_SIGNATURE, test_signature).replace(CONTEXT, context)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    test_fix = []
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=2048, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=10, eos_token_id=tokenizer.eos_token_id)
    for output in outputs:
        text_gen = test_signature + '\n' + tokenizer.decode(output, skip_special_tokens=True)[len(input_text) - len(EOT):]
        test = utils.extract_test_method(text_gen)
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

    test_incomplete = utils.extract_test_incomplete(test_fix)
    input_text = enhance_generate_prompt.replace(FOCAL_TGT_COV, focal_tgt_cov).replace(TEST_FIX, test_fix).replace(ENHANCE_RESPONSE, cot_response).replace(TEST_INCOMPLETE, test_incomplete)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=5, eos_token_id=tokenizer.eos_token_id)
    for output in outputs:
        text_gen = test_incomplete + tokenizer.decode(output, skip_special_tokens=True)[len(input_text) - 2 * len(EOT):]
        test = utils.extract_test_method(text_gen)
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

def invoke_model(focal_src, focal_tgt, test_src):
    focal_src = '\n'.join([utils.align_code(x) for x in focal_src])
    focal_tgt = '\n'.join([utils.align_code(x) for x in focal_tgt])
    test_src = utils.align_code(test_src)
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
        sample_dict = utils.read_json(os.path.join(data_path, file))
        for key, value in tqdm(sample_dict.items()):
            test_id = value['test_id']
            commit_tgt = value['commit_tgt']
            focal_path_src = value['focal_path_src']
            focal_src = value['focal_src']
            focal_tgt = value['focal_tgt']
            test_src = value['test_src_code']
            call_codes = value['call_codes']
            focal_src_aligned = '\n'.join([utils.align_code(x) for x in focal_src])
            focal_tgt_aligned = '\n'.join([utils.align_code(x) for x in focal_tgt])
            test_src_aligned = utils.align_code(test_src)
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
                        related_prod, related_tests = utils.extract_related_methods(evosuite_output_path, target_methods)
                        context = utils.get_context_with_specified_body(work_dir, focal_path_src, related_prod)
                    else:
                        context = utils.get_context_with_specified_body(work_dir, focal_path_src, [])
                    call_code_context = utils.get_call_code_context(call_codes)
                    test_fix = fix_test(context, call_code_context, focal_src_aligned, focal_tgt_aligned, test_src_aligned)
                    utils.checkout(pid, f'{test_id}t', work_dir, commit_tgt)
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
                    test_fix, focal_tgt_cov = utils.rank_by_cov(test_fix, focal_tgt_cov)
                    print(f"len(test_fix)={len(test_fix)}")
                    if len(test_fix) == 0:
                        test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
                    value['test_fix_deepseek-coder'] = test_fix
            except Exception as e:
                traceback.print_exc()
                test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
                value['test_fix_deepseek-coder'] = test_fix
                value['exception_while_gen_deepseek-coder'] = repr(e)

        utils.write_json(os.path.join(output_dir, file), sample_dict)

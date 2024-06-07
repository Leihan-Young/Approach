import json
import os
import torch
import javalang
import re
import copy
import subprocess as sp
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import infer_auto_device_map, dispatch_model
from accelerate.utils import get_balanced_memory

cov_cli_path = "/workspace/GHRB_test_co-evolution"
repos_path = "/workspace/GHRB_test_co-evolution/collected/raw_repos"
model_path = "/workspace/DeepSeekCoder/deepseek-coder-6.7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)

FOCAL_SRC = "$FOCAL_SRC$"
FOCAL_TGT = "$FOCAL_TGT$"
FOCAL_TGT_COV = "$FOCAL_TGT_COV$"
TEST_SRC = "$TEST_SRC$"
TEST_FIX = "$TEST_FIX$"
TEST_PREFIX = "$TEST_PREFIX$"
TEST_SIGNATURE = "$TEST_SIGNATURE$"
TEST_INCOMPLETE = "$TEST_INCOMPLETE$"
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
// The updated version of the test code that co-evolves with the production code
### Response:
{TEST_SIGNATURE}
"""

enhance_prompt = f"""You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
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


def extract_test_signature(test):
    ind = test.find('{')+1
    signature = test[:ind]
    if test[ind+1:].lstrip().startswith('\n'):
        suf = test[ind+1:]
        signature += suf[:suf.find('\n')]
    return signature

def extract_test_incomplete(test):
    ind = test.rfind('}')
    return test[:ind]

def evaluate_cov(tests, pid, focal_path, focal_code_):
    focal_code = copy.deepcopy(focal_code_)
    cov_res = []
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')
    if not os.path.exists('./output'):
        os.makedirs('./output')
    command = f"python cli.py clean -w {os.path.join(repos_path, pid)}"
    run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
    print(run.stdout.decode())
    for test in tests:
        with open('./tmp/input.java', 'w', encoding='utf-8') as f:
            f.write(test)
        command = f"python cli.py coverage -w {os.path.join(repos_path, pid)} -o {os.path.abspath('./output')} -i {os.path.abspath('./tmp/input.java')}"
        run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cov_cli_path, shell=True)
        print(run.stdout.decode())
        if "BUILD FAILURE" in run.stdout.decode():
            cov_res.append(None)
            continue
        cov = []
        for idx1, path in enumerate(focal_path):
            cov_html_file = os.path.join('./output', f'{path[path.rfind("/")+1:].split("#")[0]}.html')
            with open(cov_html_file, 'r', encoding='utf-8') as f:
                cov_html_lines = f.readlines()
            src_lines = focal_code[idx1].split('\n')
            for idx2, line in enumerate(cov_html_lines):
                if src_lines[0] in line and len(cov_html_lines) > idx2+len(src_lines)-1 and src_lines[len(src_lines)-1] in cov_html_lines[idx2+len(src_lines)-1]:
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

def countSymbol(line, symbol):
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
        left_count = countSymbol(lines[end], '{')
        right_count = countSymbol(lines[end], '}')
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

def fix_test(focal_src, focal_tgt, test_src):
    test_signature = extract_test_signature(test_src)
    input_text = fix_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src).replace(TEST_SIGNATURE, test_signature)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    if inputs.input_ids.shape[1] > 7500:
        raise Exception("No enough memory for inference")
    test_fix = []
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=True, top_k=50, top_p=0.9, num_return_sequences=5, eos_token_id=tokenizer.eos_token_id)
    for output in outputs:
        text_gen = test_signature + '\n' + tokenizer.decode(output, skip_special_tokens=True)[len(input_text) - len(EOT):]
        test = extract_test_method(text_gen)
        if test is not None:
            test_fix.append(test)
    return test_fix

def enhance_test(focal_tgt, test_fix):
    test_enhance = []
    for idx, focal_code_cov in enumerate(focal_tgt):
        if focal_code_cov is None:
            test_enhance.append(None)
            continue
        focal_tgt_cov = '\n'.join(focal_code_cov)
        if not ("Not Covered" in focal_tgt_cov or "Partially Covered" in focal_tgt_cov):
            test_enhance.append(test_fix[idx])
            continue
        test_incomplete = extract_test_incomplete(test_fix[idx])
        input_text = enhance_prompt.replace(FOCAL_TGT_COV, focal_tgt_cov).replace(TEST_FIX, test_fix[idx]).replace(TEST_INCOMPLETE, test_incomplete)
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
        if inputs.input_ids.shape[1] > 7500:
            raise Exception("No enough memory for inference")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=False, top_k=50, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
        text_gen = test_incomplete + tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text) - len(EOT):]
        test = extract_test_method(text_gen)
        if test is not None:
            test_enhance.append(test)
    return test_enhance

def identify_obsolete(focal_src, focal_tgt, test_src):
    input_text = identify_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    if inputs.input_ids.shape[1] > 7500:
        raise Exception("No enough memory for inference")
    test_fix = []
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256, do_sample=False, top_k=50, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
    text_gen = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text) - len(EOT):]
    obsolete = True
    print(text_gen)
    if text_gen.startswith('No'):
        obsolete = False
    return obsolete

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
    data_path = '/workspace/GHRB_test_co-evolution/verified'
    output_dir = './data'
    files = [name for name in os.listdir(data_path)
                if name.endswith('.json')]
    for idx, file in enumerate(files):
        if os.path.exists(os.path.join(output_dir, file)):
            continue
        print(file)
        pid = file.split('_')[-1].replace('.json', '')
        work_dir = f'/workspace/GHRB_test_co-evolution/collected/raw_repos/{pid}'
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

            try:
                print(f"{pid}:{test_id}")
                identified = identify_obsolete(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
                value['identify_result_deepseek-coder'] = identified
                if identified:
                    test_fix = fix_test(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
                    checkout(pid, f'{test_id}t', work_dir, commit_tgt)
                    focal_tgt_cov = evaluate_cov(test_fix, pid, focal_path_src, focal_tgt)
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
                        test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                    else:
                        test_enhance = enhance_test(focal_tgt_cov, test_fix)
                        focal_tgt_cov_enhance = evaluate_cov(test_enhance, pid, focal_path_src, focal_tgt)
                        tmp_test_enhance = []
                        tmp_focal_tgt_cov_enhance = []
                        for idx, focal_tgt_cov_enhance_item in enumerate(focal_tgt_cov_enhance):
                            if focal_tgt_cov_enhance_item is None:
                                continue
                            tmp_test_enhance.append(test_enhance[idx])
                            tmp_focal_tgt_cov_enhance.append(focal_tgt_cov_enhance_item)
                        test_enhance = tmp_test_enhance
                        focal_tgt_cov_enhance = tmp_focal_tgt_cov_enhance
                        test_fix, _ = rank_by_cov(test_fix, focal_tgt_cov)
                        print(f"len(test_enhance)={len(test_enhance)}")
                        if len(test_enhance) == 0:
                            test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                        else:
                            test_enhance, _ = rank_by_cov(test_enhance, focal_tgt_cov_enhance)
                    value['test_fix_deepseek-coder'] = test_fix
                    value['test_enhance_deepseek-coder'] = test_enhance
            except Exception as e:
                print(repr(e))
                test_fix = ['// Fail to generate test fix. This is original test code.\n' + test_src_aligned]
                test_enhance = ['// Fail to generate test enhance. This is original test code.\n' + test_src_aligned]
                value['test_fix_deepseek-coder'] = test_fix
                value['test_enhance_deepseek-coder'] = test_enhance
                value['exception_while_gen_deepseek-coder'] = repr(e)

        write_json(os.path.join(output_dir, file), sample_dict)


    # pid = "shardingsphere"
    # test_id = '1'
    # commit_tgt = '871cedbd12c4639a845929b37bf64c9195187fd1'
    # work_dir = f'/workspace/GHRB_test_co-evolution/collected/raw_repos/{pid}'
    # focal_path_src = ["proxy/bootstrap/src/main/java/org/apache/shardingsphere/proxy/database/DatabaseServerInfo.java#DatabaseServerInfo",
    #   "proxy/bootstrap/src/main/java/org/apache/shardingsphere/proxy/database/DatabaseServerInfo.java#toString"]
    # focal_src = ["    public DatabaseServerInfo(final DataSource dataSource) {\n        try (Connection connection = dataSource.getConnection()) {\n            DatabaseMetaData databaseMetaData = connection.getMetaData();\n            databaseName = databaseMetaData.getDatabaseProductName();\n            databaseVersion = databaseMetaData.getDatabaseProductVersion();\n        } catch (final SQLException ex) {\n            throw new DatabaseServerLoadingServerException(ex);\n        }\n    }\n",
    #   "    @Override\n    public String toString() {\n        return String.format(\"Database name is `%s`, version is `%s`\", databaseName, databaseVersion);\n    }\n"]
    # focal_tgt = ["    public DatabaseServerInfo(final DataSource dataSource) {\n        try (Connection connection = dataSource.getConnection()) {\n            DatabaseMetaData databaseMetaData = connection.getMetaData();\n            databaseType = databaseMetaData.getDatabaseProductName();\n            databaseVersion = databaseMetaData.getDatabaseProductVersion();\n        } catch (final SQLException ex) {\n            throw new DatabaseServerLoadingServerException(ex);\n        }\n    }\n",
    #   "    @Override\n    public String toString() {\n        return String.format(\"Database type is `%s`, version is `%s`\", databaseType, databaseVersion);\n    }\n"]
    # test_src = "    @Test\n    void assertToString() throws SQLException {\n        DatabaseMetaData databaseMetaData = mock(DatabaseMetaData.class);\n        when(databaseMetaData.getDatabaseProductName()).thenReturn(\"fixtureDB\");\n        when(databaseMetaData.getDatabaseProductVersion()).thenReturn(\"1.0.0\");\n        when(dataSource.getConnection().getMetaData()).thenReturn(databaseMetaData);\n        assertThat(new DatabaseServerInfo(dataSource).toString(), is(\"Database name is `fixtureDB`, version is `1.0.0`\"));\n    }\n"
    # focal_src_aligned = '\n'.join([align_code(x) for x in focal_src])
    # focal_tgt_aligned = '\n'.join([align_code(x) for x in focal_tgt])
    # test_src_aligned = align_code(test_src)
    # if identify_obsolete(focal_src_aligned, focal_tgt_aligned, test_src_aligned):
    #     test_fix = fix_test(focal_src_aligned, focal_tgt_aligned, test_src_aligned)
    #     print(test_fix)
    #     checkout(pid, f'{test_id}t', work_dir, commit_tgt)
    #     focal_tgt_cov = evaluate_cov(test_fix, pid, focal_path_src, focal_tgt)
    #     test_enhance = enhance_test(focal_tgt_cov, test_fix)
    #     for idx, x in enumerate(test_enhance):
    #         print(f"================================\n{idx}:")
    #         print(x)
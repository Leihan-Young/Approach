import json
import os
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import infer_auto_device_map, dispatch_model
from accelerate.utils import get_balanced_memory

model_path = "/nasdata/Model/deepseek-coder-6.7b-base"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)

FOCAL_SRC = "$FOCAL_SRC$"
FOCAL_TGT = "$FOCAL_TGT$"
TEST_SRC = "$TEST_SRC$"
TEST_PREFIX = "$TEST_PREFIX$"
TEST_SIGNATURE = "$TEST_SIGNATURE$"

fix_prompt = f"""// The old version of the production code
{FOCAL_SRC}
// The old version of the test code that tests the old version of the production code
{TEST_SRC}
// The updated version of the production code
{FOCAL_TGT}
// The updated version of the test code that co-evolves with the production code
{TEST_SIGNATURE}
"""

enhance_prompt = f"""
// The old version of the production code
{FOCAL_SRC}
// The updated version of the production code
{FOCAL_TGT}
// The updated version of the test code
{TEST_PREFIX}
    // To cover the uncovered statements in the updated version of the production code
    """

def split_test(test):
    '''
    public void test(){
        statement_1;
        statement_2;
        ...
        statement_n;
    }
    ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    prefix:
    public void test(){
        statement_1;
        statement_2;
        ...
        statement_n;
    suffix:
    }
    '''
    prefix = test[:test.rfind('}')]
    suffix = test[test.rfind('}'):]
    return prefix, suffix

def format(prefix, suffix):
  return "<|fim_begin|>" + prefix + "<|fim_hole|>" + suffix + "<|fim_end|>"

def post_process(prefix, test, suffix):
    test = prefix + test
    if test.find('<eom>') == -1:
        test = test.lstrip() + suffix
    else:
        test = test[:test.find('<eom>')].lstrip()
    test_lines = test.split('\n')
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
    end = 1
    comment = False
    count = countSymbol(test_lines[0], '{')
    end = end - 1
    while end + 1 < len(test_lines):
        end = end + 1
        if comment and test_lines[end].find('*/') != -1:
            comment = False
            continue
        if test_lines[end].find('/*') != -1 and test_lines[end].find('*/') == -1 and test_lines[end][:test_lines[end].find('/*')].find('"') == -1 and test_lines[end][:test_lines[end].find('/*')].find('}') == -1:
            comment = True
            continue
        left_count = countSymbol(test_lines[end], '{')
        right_count = countSymbol(test_lines[end], '}')
        diff = left_count - right_count
        if count == None and diff != 0:
            count = diff
        elif count != None:
            count = count + diff
        if count != None and count <= 0:
            break
    if test_lines[end].find('/*') != -1 and test_lines[end][:test_lines[end].find('/*')].find('"') == -1 and test_lines[end][:test_lines[end].find('/*')].find('}') == -1:
        test_lines[end] = test_lines[end][:test_lines[end].find('}') + 1]
    if test_lines[end].endswith('\n'):
        test_lines[end] = test_lines[end][:-1]
    while count > 0:
        test_lines[end] += '}'
        count -= 1
    test_lines[end] += '\n'
    end = end + 1
    if end < len(test_lines):
        test_lines = test_lines[:end]
    if test_lines[-1].lstrip().startswith('}'):
        test_lines[0] = test_lines[-1][:test_lines[-1].find('}')] + test_lines[0]
    post_test = align_code("\n".join(test_lines))
    return post_test

def extract_test_signature(test):
    ind = test.find('{')+1
    signature = test[:ind]
    if test[ind+1:].lstrip().startswith('\n'):
        suf = test[ind+1:]
        signature += suf[:suf.find('\n')+1]
    else:
        signature += '\n'
    return signature

def fix_test(focal_src, focal_tgt, test_src):
    test_signature = extract_test_signature(test_src)
    input_text = fix_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src).replace(TEST_SIGNATURE, test_signature)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    if inputs.input_ids.shape[1] > 7000:
        raise "No enough memory for inference"
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256)
    test_fix = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text):]
    test_fix = test_signature + test_fix
    return test_fix

def enhance_test(focal_src, focal_tgt, test_src):
    test_prefix = test_src[:test_src.rfind('}')]
    input_text = enhance_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_PREFIX, test_prefix)
    print(model.device)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=256)
    test_enhance = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(input_text):]
    test_enhance = test_prefix + test_enhance
    return test_enhance

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
    # print(test_fix)
    # print('--------------------------------------------------------')
    # test_enhance = enhance_test(focal_src, focal_tgt, test_fix)
    # print(test_enhance)
    return test_fix, None

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
    output_dir = './output'
    files = [name for name in os.listdir(data_path)
                if name.endswith('.json')]
    for idx, file in enumerate(files):
        if os.path.exists(os.path.join(output_dir, file)):
            continue
        print(file)
        sample_dict = read_json(os.path.join(data_path, file))
        for key, value in tqdm(sample_dict.items()):
            focal_src = value['focal_src']
            focal_tgt = value['focal_tgt']
            test_src = value['test_src_code']
            try:
                test_fix, test_enhance = invoke_model(focal_src, focal_tgt, test_src)
            except Exception as e:
                value['error_in_deepseek-coder-6.7b-base'] = repr(e)
                continue
            value['test_fix_deepseek-coder-6.7b-base'] = test_fix
        write_json(os.path.join(output_dir, file), sample_dict)


    # focal_src = ["    /**\n     * Instance deregister, mark unregistering status as {@code true}.\n     *\n     * @param serviceName service name\n     * @param groupName   group name\n     */\n    public void instanceDeregister(String serviceName, String groupName) {\n        String key = NamingUtils.getGroupedName(serviceName, groupName);\n        synchronized (registeredInstances) {\n            InstanceRedoData redoData = registeredInstances.get(key);\n            if (null != redoData) {\n                redoData.setUnregistering(true);\n            }\n        }\n    }\n"]
    # focal_tgt = ["    /**\n     * Instance deregister, mark unregistering status as {@code true}.\n     *\n     * @param serviceName service name\n     * @param groupName   group name\n     */\n    public void instanceDeregister(String serviceName, String groupName) {\n        String key = NamingUtils.getGroupedName(serviceName, groupName);\n        synchronized (registeredInstances) {\n            InstanceRedoData redoData = registeredInstances.get(key);\n            if (null != redoData) {\n                redoData.setUnregistering(true);\n                redoData.setExpectedRegistered(false);\n            }\n        }\n    }\n"]
    # test_src = "    @Test\n    public void testInstanceDeregister() {\n        ConcurrentMap<String, InstanceRedoData> registeredInstances = getInstanceRedoDataMap();\n        redoService.cacheInstanceForRedo(SERVICE, GROUP, new Instance());\n        redoService.instanceDeregister(SERVICE, GROUP);\n        InstanceRedoData actual = registeredInstances.entrySet().iterator().next().getValue();\n        assertTrue(actual.isUnregistering());\n    }\n"
    # test_fix, test_enhance = invoke_model(focal_src, focal_tgt, test_src)
    # with open('./fix.java', 'w', encoding='utf-8') as f:
    #     f.write(test_fix)
    # with open('./enhance.java', 'w', encoding='utf-8') as f:
    #     f.write(test_enhance)
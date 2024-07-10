import os
import json
import requests
import javalang
import subprocess as sp
from tqdm import tqdm

setup_project_path = None

def get_call_code_context(call_codes):
    ctx = ""
    for call_code in call_codes:
        if len(call_code) == 0:
            continue
        ctx += call_code[0]['call_method_code'] + '\n'
    return ctx

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

def set_up_language_server_helper(project_path):
    global setup_project_path
    if project_path == setup_project_path:
        return True
    url = f"http://127.0.0.1:21185/v1/api/project/setup?project_path={project_path}&language=java"
    response = requests.post(url)
    if response.status_code != 200:
        return False
    setup_project_path = project_path
    return True

def method_call_relationship_analysis():
    global setup_project_path
    if setup_project_path == None:
        return None
    url = f"http://127.0.0.1:21185/v1/api/project/call?project_path={setup_project_path}&language=java"
    response = requests.post(url)
    if response.status_code != 200:
        return None
    return response.json()

def extract_call_codes(json_relationship, class_name, method_name, method_body):
    if json_relationship == None:
        return []
    class_row = None
    for row in json_relationship:
        if row['class_name'] == class_name:
            class_row = row
            break
    if class_row == None:
        return []
    flag_row = None
    while method_body[-1].rstrip() == "":
        method_body = method_body[:-1]
    for method in class_row['methods']:
        if method['method_name'] == method_name:
            if method['method_code'] == method_body:
                return method["call_codes"]
            flag_row = method
    return [] if flag_row is None else flag_row['call_codes']

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
                ind += 1
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
        i = start
        res_line = java_code[start]
        if res_line.find('//') != -1:
            res_line = res_line[:res_line.find('//')] + '\n'
        while count_symbol(res_line, '{') == 0:
            i = i + 1
            res_line += java_code[i]
            if res_line.find('//') != -1:
                res_line = res_line[:res_line.find('//')] + '\n'
        res_line = res_line[:res_line.find('{')].rstrip() + ';\n'
        return res_line

def extract_test_signature(test):
    ind = test.find('{')
    signature = test[:ind]
    if test[ind+1:].lstrip().startswith('\n'):
        suf = test[ind+1:]
        signature += suf[:suf.find('\n')]
    return signature

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

# for __main__
def append_call_relationship(data_path, output_path):
    files = [name for name in os.listdir(data_path)
                if name.endswith('.json')]
    for idx, file in enumerate(files):
        if os.path.exists(os.path.join(output_path, file)):
            continue
        print(file)
        pid = file.split('_')[-1].replace('.json', '')
        sample_dict = read_json(os.path.join(data_path, file))
        for key, value in tqdm(sample_dict.items()):
            test_id = value['test_id']
            if test_id != 60:
                continue
            focal_path_tgt = value['focal_path_tgt']
            focal_tgt = value ['focal_tgt']
            work_dir = f'/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors/{pid}/{test_id}t'
            value["call_codes"] = []
            for idx, p in enumerate(focal_path_tgt):
                if idx >= len(focal_tgt):
                    break
                module = p.split('src/main')[0]
                project_path = os.path.join(work_dir, module, "src/main")
                while not set_up_language_server_helper(project_path):
                    continue
                call_analysis_result = method_call_relationship_analysis()
                call_codes = extract_call_codes(call_analysis_result, p.split('#')[0].split('/')[-1].replace('.java', ''), p.split('#')[-1], focal_tgt[idx])
                value["call_codes"].append(call_codes)
        write_json(os.path.join(output_path, file), sample_dict)

if __name__ == "__main__":
    append_call_relationship('/data/zhiquanyang/Co-evolution/Benchmark/verified', './data_with_call_codes')
    # setup_res = set_up_language_server_helper('/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors/nacos/1t/client/src/main')
    # x = method_call_relationship_analysis()
    # call_codes = extract_call_codes(x, 'NamingGrpcRedoService', 'instanceDeregister', "    /**\n     * Instance deregister, mark unregistering status as {@code true}.\n     *\n     * @param serviceName service name\n     * @param groupName   group name\n     */\n    public void instanceDeregister(String serviceName, String groupName) {\n        String key = NamingUtils.getGroupedName(serviceName, groupName);\n        synchronized (registeredInstances) {\n            InstanceRedoData redoData = registeredInstances.get(key);\n            if (null != redoData) {\n                redoData.setUnregistering(true);\n                redoData.setExpectedRegistered(false);\n            }\n        }\n    }\n")
    # print('pause')
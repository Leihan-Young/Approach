import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained("/workspace/codegen2-7B_P")
model = AutoModelForCausalLM.from_pretrained("/workspace/codegen2-7B_P", device_map="auto")

FOCAL_SRC = "$FOCAL_SRC$"
FOCAL_TGT = "$FOCAL_TGT$"
TEST_SRC = "$TEST_SRC$"
TEST_PREFIX = "$TEST_PREFIX$"

fix_prompt = f"""// The old version of the production code
{FOCAL_SRC}
// The old version of the test code that tests the old version of the production code
{TEST_SRC}
// The updated version of the production code
{FOCAL_TGT}
// The updated version of the test code that fixes the potential errors in the old version of the test code
"""
enhance_prompt = f"""
// The old version of the production code
{FOCAL_SRC}
// The updated version of the production code
{FOCAL_TGT}
// The updated version of the test code
{TEST_PREFIX}
// To cover the updated part of the production code
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
  return prefix + "<mask_1>" + suffix + "<|endoftext|>" + "<sep>" + "<mask_1>"

def fix_test_src(focal_src, focal_tgt, test_src):
    input_text = fix_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_SRC, test_src)
    input_text = format(input_text, '}')
    input_ids = tokenizer(input_text, return_tensors='pt').input_ids.to(device)
    generated_ids = model.generate(input_ids, max_new_tokens=256)
    test_fix = tokenizer.decode(generated_ids[0], skip_special_tokens=True)[len(input_text):]
    test_fix += '}'
    return test_fix

def enhance_test_src(focal_src, focal_tgt, test_src):
    test_prefix, test_suffix = split_test(test_src)
    input_text = enhance_prompt.replace(FOCAL_SRC, focal_src).replace(FOCAL_TGT, focal_tgt).replace(TEST_PREFIX, test_prefix)
    input_text = format(test_prefix, test_suffix)
    input_ids = tokenizer(input_text, return_tensors='pt').input_ids.to(device)
    generated_ids = model.generate(input_ids, max_new_tokens=256)
    test_enhance = tokenizer.decode(generated_ids[0], skip_special_tokens=True)[len(input_text):]
    test_enhance += test_suffix
    return test_enhance

def align_test(test):
    test_lines = test.split('\n')
    move = len(test_lines[0]) - len(test_lines[0].lstrip())
    for i in range(len(test_lines)):
        if move > len(test_lines[i]) - len(test_lines[i].lstrip()):
            move = len(test_lines[i]) - len(test_lines[i].lstrip())
    aligned_test = [l[move:] for l in test_lines]
    return '\n'.join(aligned_test)

def main(focal_src, focal_tgt, test_src):
    test_src = align_test(test_src)
    test_fix = fix_test_src(focal_src, focal_tgt, test_src)
    print(f"""
          test_fix=
          {test_fix}
          ---------------------------------------------
          """)
    test_enhance = enhance_test_src(focal_src, focal_tgt, test_fix)
    print(f"""
          test_enhance=
          {test_enhance}
          ---------------------------------------------
          """)
    return test_enhance
    
if __name__ == "__main__":
    focal_src = "    @Override\n    public String execute(CommandContext commandContext) throws NoSuchCommandException {\n        BaseCommand command = null;\n        try {\n            command = frameworkModel.getExtensionLoader(BaseCommand.class).getExtension(commandContext.getCommandName());\n        } catch (Throwable throwable) {\n                //can't find command\n        }\n        if (command == null) {\n            throw new NoSuchCommandException(commandContext.getCommandName());\n        }\n        return command.execute(commandContext, commandContext.getArgs());\n    }\n"
    focal_tgt = "    @Override\n    public String execute(CommandContext commandContext) throws NoSuchCommandException, PermissionDenyException {\n        BaseCommand command = null;\n        try {\n            command = frameworkModel.getExtensionLoader(BaseCommand.class).getExtension(commandContext.getCommandName());\n        } catch (Throwable throwable) {\n                //can't find command\n        }\n        if (command == null) {\n            throw new NoSuchCommandException(commandContext.getCommandName());\n        }\n\n        // check permission when configs allow anonymous access\n        if (commandContext.isAllowAnonymousAccess()) {\n            PermissionChecker permissionChecker = DefaultAnonymousAccessPermissionChecker.INSTANCE;\n            try {\n                permissionChecker = frameworkModel.getExtensionLoader(PermissionChecker.class).getExtension(QosConstants.QOS_PERMISSION_CHECKER);\n            } catch (Throwable throwable) {\n                //can't find valid custom permissionChecker\n            }\n\n            final Cmd cmd = command.getClass().getAnnotation(Cmd.class);\n            final PermissionLevel cmdRequiredPermissionLevel = cmd.requiredPermissionLevel();\n\n            if (!permissionChecker.access(commandContext, cmdRequiredPermissionLevel)) {\n                throw new PermissionDenyException(commandContext.getCommandName());\n            }\n        }\n\n        return command.execute(commandContext, commandContext.getArgs());\n    }\n"
    test_src = "    @Test\n    void testExecute2() throws Exception {\n        DefaultCommandExecutor executor = new DefaultCommandExecutor(FrameworkModel.defaultModel());\n        String result = executor.execute(CommandContextFactory.newInstance(\"greeting\", new String[]{\"dubbo\"}, false));\n        assertThat(result, equalTo(\"greeting dubbo\"));\n    }\n"
    test_tgt = main(focal_src, focal_tgt, test_src)
    with open('./try.java', 'w', encoding='utf-8') as f:
        f.write(test_tgt)
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("/workspace/codegen-6B-multi")
model = AutoModelForCausalLM.from_pretrained("/workspace/codegen-6B-multi")
fix_prompt = f"// The old version of the production code\n\
    $FOCAL_SRC$\n\
    //The old version of the test code that tests the old version of the production code\
    $TEST_SRC$
    // The updated version of the production code\n\
    $FOCAL_TGT$\n\
    // The updated version of the test code that fixes the potential errors in the old version of the test code\n\
    "
cov_prompt = ""

if __name__ == "__main__":
    focal_src = '    @Override\n    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) throws Exception {\n        if (in.readableBytes() < 1) {\n            return;\n        }\n\n        // read one byte to guess protocol\n        final int magic = in.getByte(in.readerIndex());\n\n        ChannelPipeline p = ctx.pipeline();\n        p.addLast(new LocalHostPermitHandler(acceptForeignIp));\n        if (isHttp(magic)) {\n            // no welcome output for http protocol\n            if (welcomeFuture != null && welcomeFuture.isCancellable()) {\n                welcomeFuture.cancel(false);\n            }\n            p.addLast(new HttpServerCodec());\n            p.addLast(new HttpObjectAggregator(1048576));\n            p.addLast(new HttpProcessHandler(frameworkModel));\n            p.remove(this);\n        } else {\n            p.addLast(new LineBasedFrameDecoder(2048));\n            p.addLast(new StringDecoder(CharsetUtil.UTF_8));\n            p.addLast(new StringEncoder(CharsetUtil.UTF_8));\n            p.addLast(new IdleStateHandler(0, 0, 5 * 60));\n            p.addLast(new TelnetIdleEventHandler());\n            p.addLast(new TelnetProcessHandler(frameworkModel));\n            p.remove(this);\n        }\n    }\n'
    focal_tgt = '    @Override\n    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) throws Exception {\n        if (in.readableBytes() < 1) {\n            return;\n        }\n\n        // read one byte to guess protocol\n        final int magic = in.getByte(in.readerIndex());\n\n        ChannelPipeline p = ctx.pipeline();\n        p.addLast(new ForeignHostPermitHandler(acceptForeignIp, acceptForeignIpWhitelist));\n        if (isHttp(magic)) {\n            // no welcome output for http protocol\n            if (welcomeFuture != null && welcomeFuture.isCancellable()) {\n                welcomeFuture.cancel(false);\n            }\n            p.addLast(new HttpServerCodec());\n            p.addLast(new HttpObjectAggregator(1048576));\n            p.addLast(new HttpProcessHandler(frameworkModel));\n            p.remove(this);\n        } else {\n            p.addLast(new LineBasedFrameDecoder(2048));\n            p.addLast(new StringDecoder(CharsetUtil.UTF_8));\n            p.addLast(new StringEncoder(CharsetUtil.UTF_8));\n            p.addLast(new IdleStateHandler(0, 0, 5 * 60));\n            p.addLast(new TelnetIdleEventHandler());\n            p.addLast(new TelnetProcessHandler(frameworkModel));\n            p.remove(this);\n        }\n    }\n'
    test_src = "    @Test\n    void testDecodeHttp() throws Exception {\n        ByteBuf buf = Unpooled.wrappedBuffer(new byte[] {'G'});\n        ChannelHandlerContext context = Mockito.mock(ChannelHandlerContext.class);\n        ChannelPipeline pipeline = Mockito.mock(ChannelPipeline.class);\n        Mockito.when(context.pipeline()).thenReturn(pipeline);\n        QosProcessHandler handler = new QosProcessHandler(FrameworkModel.defaultModel(), \"welcome\", false);\n        handler.decode(context, buf, Collections.emptyList());\n        verify(pipeline).addLast(any(HttpServerCodec.class));\n        verify(pipeline).addLast(any(HttpObjectAggregator.class));\n        verify(pipeline).addLast(any(HttpProcessHandler.class));\n        verify(pipeline).remove(handler);\n    }\n"
    fix_input_text = fix_prompt.replace('$FOCAL_SRC$', focal_src).replace('$FOCAL_TGT$', focal_tgt).replace('$TEST_SRC$', test_src)
    input_ids = tokenizer(fix_input_text, return_tensors='pt').input_ids
    generated_ids = model.generate(input_ids, max_length=1024)
    test_fix = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    with open('./try.java', 'w', encoding='utf-8') as f:
        f.write(test_fix)
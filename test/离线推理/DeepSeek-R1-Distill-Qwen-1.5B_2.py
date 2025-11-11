from vllm import LLM, SamplingParams

llm = LLM(
    model="/root/autodl-tmp/vllm/deepseek-ai/DeepSeek-R1-Distill-Qwen-1___5B",
    trust_remote_code=True,
    max_model_len=4096,
    gpu_memory_utilization=0.5,
)

prompts = "你好，请介绍一下你自己。"

# ✅ 显式指定采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,              # 设置足够长的输出
    skip_special_tokens=False,   # 保留 <think> 标记以查看思考过程
    # 或者设置为 True 来隐藏思考过程
)

print("\n" + "="*50)
print("开始推理测试...")
print("="*50 + "\n")

outputs = llm.generate(prompts, sampling_params=sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"提示词: {prompt}")
    print(f"生成结果: {generated_text}")
    print(f"生成 tokens 数: {len(output.outputs[0].token_ids)}")
    print(f"结束原因: {output.outputs[0].finish_reason}")
    print("-" * 50)
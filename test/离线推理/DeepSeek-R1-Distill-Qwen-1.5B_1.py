from vllm import LLM, SamplingParams

# 创建 LLM 实例
llm = LLM(model="/root/autodl-tmp/vllm/deepseek-ai/DeepSeek-R1-Distill-Qwen-1___5B",
          trust_remote_code=True,
          max_model_len=4096,
          gpu_memory_utilization=0.5,  # ← 关键参数！限制为 50%
)

# 添加测试推理
prompts = "你好，请介绍一下你自己。"


# 执行推理
print("\n" + "="*50)
print("开始推理测试...")
print("="*50 + "\n")

outputs = llm.generate(prompts)

# 打印结果
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"提示词: {prompt}")
    print(f"生成结果: {generated_text}")
    print("-" * 50)
from vllm import LLM, SamplingParams  # ← 1. 导入 SamplingParams

llm = LLM(
    model="/root/autodl-tmp/vllm/zpeng1989/Medical_Qwen3_8B_Large_Language_Model",
    trust_remote_code=True,
    gpu_memory_utilization=0.8,
    max_model_len=4096,
)

# 2. 添加 SamplingParams 指定生成长度
sampling_params = SamplingParams(
    temperature=0.6,
    top_p=0.9,
    max_tokens=2048,              # 指定最大生成 512 tokens
    skip_special_tokens=True,
)

# 3. 传入 sampling_params
outputs = llm.generate("你好，请你介绍一下你自己", sampling_params=sampling_params)

for output in outputs:
    generated_text = output.outputs[0].text
    print(f"Generated text: {generated_text!r}")
    print(f"生成 tokens 数: {len(output.outputs[0].token_ids)}")
    print(f"结束原因: {output.outputs[0].finish_reason}")
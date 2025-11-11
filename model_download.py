#模型下载
from modelscope import snapshot_download
# model_dir = snapshot_download('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B', cache_dir='/root/autodl-tmp/vllm', revision='master')

# model_dir = snapshot_download('Qwen/Qwen3-4B', cache_dir='/root/autodl-tmp/vllm', revision='master')

# model_dir = snapshot_download('zpeng1989/Medical_Qwen3_8B_Large_Language_Model', cache_dir='/root/autodl-tmp/vllm', revision='master')


model_dir = snapshot_download('deepseek-ai/DeepSeek-OCR', cache_dir='/root/autodl-tmp/vllm', revision='master')


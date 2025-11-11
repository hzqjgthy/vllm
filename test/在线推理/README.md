# vLLM 在线服务文档

本目录包含 vLLM 在线服务部署的完整文档和代码。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `vLLM在线服务部署完整指南.md` | 完整的部署指南，包含原理、配置、问题排查等 |
| `vllm_client.py` | 可直接使用的客户端封装代码 |
| `README.md` | 本文件，快速入门指南 |

## 🚀 快速开始

### 1. 服务器端启动 vLLM

```bash
vllm serve /root/autodl-tmp/vllm/Qwen/Qwen3-4B \
    --served-model-name Qwen3-4B \
    --api_key muyu \
    --host 0.0.0.0 \
    --port 9000 \
    --trust_remote_code \
    --tensor_parallel_size 1
```

### 2. 本地建立 SSH 隧道

```powershell
# Windows 命令行
ssh -p 47055 -L 9000:localhost:9000 root@connect.nmb2.seetacloud.com
```

### 3. 使用客户端

#### 方式 A：复制 vllm_client.py 到你的项目

```python
from vllm_client import VLLMClient

# 创建客户端
client = VLLMClient(backend='requests')

# 简单对话
response = client.chat("你好")
print(response)
```

#### 方式 B：直接使用 requests

```python
import requests

url = "http://localhost:9000/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer muyu"
}
data = {
    "model": "Qwen3-4B",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 512
}

response = requests.post(url, headers=headers, json=data)
print(response.json()['choices'][0]['message']['content'])
```

#### 方式 C：使用 OpenAI SDK

```python
from openai import OpenAI
import httpx

# 必须配置完整的 httpx 参数！
http_client = httpx.Client(
    timeout=120.0,
    limits=httpx.Limits(
        max_keepalive_connections=0,
        max_connections=100,
        keepalive_expiry=0
    ),
    transport=httpx.HTTPTransport(retries=0)
)

client = OpenAI(
    base_url="http://localhost:9000/v1",
    api_key="muyu",
    http_client=http_client
)

completion = client.chat.completions.create(
    model="Qwen3-4B",
    messages=[{"role": "user", "content": "你好"}],
    max_tokens=512
)

print(completion.choices[0].message.content)
```

## 📖 完整文档

详细信息请查看：[vLLM在线服务部署完整指南.md](./vLLM在线服务部署完整指南.md)

包含内容：
- ✅ 详细的配置说明
- ✅ 常见问题排查
- ✅ 错误处理方案
- ✅ 生产级代码示例
- ✅ FAQ 常见问题

## ⚠️ 重要提示

1. **服务器端**：必须使用 `--host 0.0.0.0`
2. **SSH 隧道**：保持终端窗口打开
3. **max_tokens**：必须显式设置（默认值只有 16）
4. **OpenAI SDK**：必须完整配置 httpx 的四个参数，缺一不可！

## 🎯 推荐方案

| 场景 | 推荐 | 原因 |
|------|------|------|
| 稳定性优先 | **requests** | 简单可靠，无兼容性问题 |
| 需要流式输出 | **OpenAI SDK** | 原生支持 stream |
| 快速开发 | **vllm_client.py** | 封装完善，开箱即用 |

## 📝 更新日志

- 2025-10-05：初始版本，包含完整的部署指南和客户端代码

## 🤝 贡献

如有问题或改进建议，请更新相关文档。

# Ollama 服务管理和 GPU 使用指南

my_inset:
    使用ollama拉取模型如果很慢，可拉取前添加镜像源：
        # 设置阿里云镜像（如果可用）
        export OLLAMA_MIRRORS="https://ollama.mirror.aliyuncs.com"
        上面的，也可以不添加镜像，停止重新下载就会接着下载，速度变快


## 📋 目录

1. [安装状态分析](#安装状态分析)
2. [停止 Ollama 服务](#停止-ollama-服务)
3. [启用 GPU 加速](#启用-gpu-加速)
4. [服务管理](#服务管理)
5. [GPU 监控和验证](#gpu-监控和验证)
6. [常见问题](#常见问题)

---

## 📊 安装状态分析

### ✅ 安装成功的组件

根据安装日志分析：

```bash
>>> Installing ollama to /usr/local
>>> Downloading Linux amd64 bundle
>>> Creating ollama user...
>>> Adding ollama user to video group...
>>> The Ollama API is now available at 127.0.0.1:11434.
>>> Install complete.
```

**成功项**：
- ✅ Ollama 主程序已安装到 `/usr/local`
- ✅ Ollama 用户和权限组已创建
- ✅ API 服务配置完成，监听 `127.0.0.1:11434`

### ⚠️ 安装警告

#### 警告 1: systemd 未运行
```
WARNING: systemd is not running
```

**原因**: Docker/AutoDL 容器环境不运行完整的 systemd 服务

**影响**: Ollama 不会作为系统服务自动启动，需要手动启动

#### 警告 2: GPU 检测失败（已解决）
```
WARNING: Unable to detect NVIDIA/AMD GPU
```

**原因**: 安装时缺少硬件检测工具 `lspci` 和 `lshw`

**解决方案**: 已通过以下命令安装
```bash
apt-get update && apt-get install -y pciutils lshw
```

---

## 🛑 停止 Ollama 服务

### 方法 1: 使用 PID 停止（推荐）

如果您知道进程 PID（启动时会显示）：

```bash
# 查看启动日志中的 PID，例如：
# [1] 11661

# 正常停止
kill 11661

# 强制停止（如果进程无响应）
kill -9 11661
```

### 方法 2: 使用 pkill 停止

```bash
# 停止所有 ollama 进程
pkill ollama

# 强制停止
pkill -9 ollama
```

### 方法 3: 使用 killall 停止

```bash
# 停止所有名为 ollama 的进程
killall ollama

# 强制停止
killall -9 ollama
```

### 验证服务已停止

```bash
# 检查 ollama 进程是否还在运行
ps aux | grep ollama

# 检查端口是否还被占用
lsof -i :11434

# 或使用 netstat
netstat -tulpn | grep 11434
```

---

## 🚀 启用 GPU 加速

### 系统 GPU 配置

您的系统配置（非常强大）：

```
硬件配置：
- 8 × NVIDIA GeForce RTX 3090 (24GB 显存)
- CUDA Version: 12.8
- Driver Version: 570.124.04
```

检测到的 GPU 列表：
```bash
$ lspci | grep -i vga
03:00.0 VGA compatible controller: ASPEED Technology, Inc. ASPEED Graphics Family
4f:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
52:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
56:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
57:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
ce:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
d1:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
d5:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
d6:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090]
```

### 启动 Ollama 服务（自动检测 GPU）

Ollama 会自动检测并使用可用的 GPU，无需特殊配置：

```bash
# 后台启动服务
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 查看启动日志
tail -f /tmp/ollama.log
```

### 指定使用特定 GPU（可选）

如果需要限制使用特定 GPU：

```bash
# 只使用 GPU 0
CUDA_VISIBLE_DEVICES=0 ollama serve

# 使用 GPU 0 和 1
CUDA_VISIBLE_DEVICES=0,1 ollama serve

# 使用 GPU 0,1,2,3
CUDA_VISIBLE_DEVICES=0,1,2,3 ollama serve

# 后台运行并指定 GPU
CUDA_VISIBLE_DEVICES=0,1 nohup ollama serve > /tmp/ollama.log 2>&1 &
```

### 验证 GPU 支持

```bash
# 查看 Ollama 版本信息
ollama --version

# 启用调试模式查看详细信息
OLLAMA_DEBUG=1 ollama serve
```

---

## 🔧 服务管理

### 启动服务

```bash
# 方式 1: 后台启动（推荐）
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 方式 2: 使用 screen 保持会话
screen -dmS ollama ollama serve

# 方式 3: 使用 tmux 保持会话
tmux new-session -d -s ollama 'ollama serve'

# 方式 4: 前台运行（调试用）
ollama serve
```

### 检查服务状态

```bash
# 检查进程是否运行
ps aux | grep ollama

# 检查 API 是否可用
curl http://127.0.0.1:11434

# 查看已安装的模型
ollama list

# 查看服务日志
tail -50 /tmp/ollama.log
```

### 模型管理

```bash
# 拉取模型
ollama pull llama2          # 7B 模型
ollama pull llama2:13b      # 13B 模型
ollama pull llama2:70b      # 70B 模型
ollama pull mistral         # Mistral 模型
ollama pull codellama       # 代码专用模型

# 列出已安装模型
ollama list

# 删除模型
ollama rm llama2

# 查看模型信息
ollama show llama2
```

### 运行模型

```bash
# 交互式运行
ollama run llama2

# 单次查询
ollama run llama2 "你好，请介绍一下深度学习"

# 使用中文提示
ollama run llama2 "请用中文解释什么是 GraphRAG"

# 退出交互模式
/bye
```

---

## 📊 GPU 监控和验证

### 实时监控 GPU 使用

打开两个终端窗口进行监控：

**终端 1 - GPU 监控**
```bash
# 每秒刷新一次 GPU 状态
watch -n 1 nvidia-smi

# 或持续监控
nvidia-smi -l 1

# 简化输出
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv -l 1
```

**终端 2 - 运行模型**
```bash
# 启动模型推理
ollama run llama2 "请详细解释一下人工智能的发展历史"
```

### GPU 使用指标说明

运行模型时，在 `nvidia-smi` 输出中观察：

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.124.04             Driver Version: 570.124.04     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3090        On  |   00000000:D1:00.0 Off |                  N/A |
| 75%   65C    P2            280W /  350W |   15234MiB / 24576MiB |     95%      Default |
+-----------------------------------------+------------------------+----------------------+
```

**关键指标**：
- **GPU-Util**: GPU 使用率（空闲时 0%，推理时通常 80-100%）
- **Memory-Usage**: 显存使用量（模型加载后会增加）
- **Temp**: 温度（通常在 60-80°C）
- **Pwr:Usage**: 功耗（空闲 ~30W，满载可达 350W）

### 验证 GPU 加速是否生效

```bash
# 1. 查看 ollama 进程是否出现在 GPU 进程列表
nvidia-smi | grep ollama

# 2. 比较推理速度
# CPU 模式下：通常几十 tokens/秒
# GPU 模式下：可达数百 tokens/秒

# 3. 观察显存使用
# 7B 模型：约 4-8GB 显存
# 13B 模型：约 8-16GB 显存
# 70B 模型：约 40-70GB 显存（可能需要多卡）
```

---

## 🔍 完整操作流程

### 初次使用流程

```bash
# 1. 停止旧服务（如果有）
pkill ollama

# 2. 启动服务
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 3. 等待几秒，查看启动日志
sleep 3
tail -20 /tmp/ollama.log

# 4. 测试 API 连接
curl http://127.0.0.1:11434/api/tags

# 5. 拉取模型
ollama pull llama2

# 6. 打开 GPU 监控（新终端）
watch -n 1 nvidia-smi

# 7. 运行模型测试
ollama run llama2 "你好，请介绍一下你自己"

# 8. 观察 GPU 使用情况
```

### 在 GraphRAG 中使用 Ollama

配置 GraphRAG 使用本地 Ollama：

```yaml
# settings.yaml 配置示例
llm:
  type: openai_chat
  api_base: http://127.0.0.1:11434/v1  # Ollama 兼容 OpenAI API
  model: llama2
  api_key: ollama  # 随意填写，Ollama 不验证

embeddings:
  type: openai_embedding
  api_base: http://127.0.0.1:11434/v1
  model: llama2
  api_key: ollama
```

或使用环境变量：

```bash
export OLLAMA_HOST=http://127.0.0.1:11434
export OPENAI_API_BASE=http://127.0.0.1:11434/v1
export OPENAI_API_KEY=ollama
```

---

## ❓ 常见问题

### Q1: 服务启动后 curl 无响应

**问题**：
```bash
$ curl http://127.0.0.1:11434
# 没有输出
```

**原因**: 服务可能还在启动中

**解决**：
```bash
# 1. 查看日志
tail -f /tmp/ollama.log

# 2. 等待几秒后重试
sleep 5
curl http://127.0.0.1:11434

# 3. 检查进程状态
ps aux | grep ollama
```

### Q2: 模型推理速度很慢

**原因**: 可能没有使用 GPU 或 GPU 配置不当

**排查**：
```bash
# 1. 运行模型时检查 GPU 使用
nvidia-smi

# 2. 查看是否有错误日志
tail -100 /tmp/ollama.log | grep -i error

# 3. 确认 CUDA 可用
python3 -c "import torch; print(torch.cuda.is_available())"

# 4. 重启服务
pkill ollama
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

### Q3: 显存不足 (Out of Memory)

**原因**: 模型太大或多个模型同时加载

**解决**：
```bash
# 1. 使用更小的模型
ollama pull llama2:7b  # 而不是 70b

# 2. 指定使用多张 GPU
CUDA_VISIBLE_DEVICES=0,1,2,3 ollama serve

# 3. 查看当前显存使用
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# 4. 停止其他 GPU 进程
# 找到占用 GPU 的进程并停止
```

### Q4: 服务莫名停止

**原因**: 可能被系统杀死或出现错误

**排查**：
```bash
# 1. 查看系统日志
dmesg | tail -50

# 2. 查看 Ollama 日志
tail -100 /tmp/ollama.log

# 3. 使用 screen 或 tmux 保持服务
screen -dmS ollama ollama serve

# 4. 添加自动重启脚本
cat > /root/start_ollama.sh << 'EOF'
#!/bin/bash
while true; do
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Ollama stopped, restarting..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
    fi
    sleep 60
done
EOF
chmod +x /root/start_ollama.sh
nohup /root/start_ollama.sh &
```

### Q5: 如何使用特定的 GPU

**需求**: 在多 GPU 系统中指定使用特定显卡

**方法**：
```bash
# 只使用第一张 RTX 3090 (GPU 0)
CUDA_VISIBLE_DEVICES=0 ollama serve

# 使用 GPU 0,2,4,6（偶数卡）
CUDA_VISIBLE_DEVICES=0,2,4,6 ollama serve

# 使用所有 GPU 除了 GPU 7
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6 ollama serve
```

### Q6: 如何在 Python 中调用 Ollama

```python
import requests
import json

def query_ollama(prompt, model="llama2"):
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
result = query_ollama("请用中文介绍一下深度学习")
print(result['response'])
```

---

## 📚 参考资源

### 官方文档
- Ollama 官网: https://ollama.ai
- GitHub: https://github.com/ollama/ollama
- 模型库: https://ollama.ai/library

### 推荐模型

| 模型名称 | 参数量 | 显存需求 | 适用场景 |
|---------|--------|---------|---------|
| llama2 | 7B | ~4GB | 通用对话、问答 |
| llama2:13b | 13B | ~8GB | 更高质量对话 |
| llama2:70b | 70B | ~40GB | 专业任务、复杂推理 |
| mistral | 7B | ~4GB | 高效推理、代码生成 |
| codellama | 7B | ~4GB | 代码生成、编程助手 |
| yi:34b | 34B | ~20GB | 中文优化模型 |
| qwen:14b | 14B | ~9GB | 中文专用模型 |

### 性能优化建议

**对于您的 8×RTX 3090 配置**：
1. 可以同时运行多个小模型（7B/13B）
2. 或运行一个大模型（70B）使用多卡
3. 建议为不同任务分配不同 GPU
4. 使用 `CUDA_VISIBLE_DEVICES` 隔离 GPU 资源

---

## 📝 维护建议

### 定期维护任务

```bash
# 1. 更新 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 清理未使用的模型
ollama list
ollama rm <unused-model>

# 3. 检查日志文件大小
ls -lh /tmp/ollama.log

# 4. 轮转日志
mv /tmp/ollama.log /tmp/ollama.log.old
pkill ollama
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 5. 监控 GPU 健康状态
nvidia-smi -q
```

### 性能监控脚本

```bash
# 创建监控脚本
cat > /root/monitor_ollama.sh << 'EOF'
#!/bin/bash
echo "=== Ollama 服务状态 ==="
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama 服务运行中"
    echo "PID: $(pgrep -x ollama)"
else
    echo "❌ Ollama 服务未运行"
fi

echo -e "\n=== GPU 使用情况 ==="
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv

echo -e "\n=== Ollama 模型列表 ==="
ollama list

echo -e "\n=== 端口监听状态 ==="
netstat -tulpn | grep 11434
EOF

chmod +x /root/monitor_ollama.sh

# 运行监控
/root/monitor_ollama.sh
```

---

**文档版本**: v1.0  
**最后更新**: 2025-10-02  
**适用环境**: Ubuntu 22.04, CUDA 12.8, 8×RTX 3090  
**作者**: AI Assistant 
# Ollama 模型从系统盘迁移到数据盘完整指南

## 📋 迁移步骤

### 步骤 1: 停止 Ollama 服务

```bash
pkill ollama
sleep 2
```

### 步骤 2: 创建数据盘目录结构

```bash
# 创建完整目录结构
mkdir -p /root/autodl-tmp/ollama/models
mkdir -p /root/autodl-tmp/ollama/logs
```

**重要**: 必须同时创建 `logs` 目录，否则启动服务时会报错！

### 步骤 3: 移动现有模型（如果有）

```bash
# 检查是否有现有模型
if [ -d "$HOME/.ollama" ]; then
    echo "发现现有 Ollama 目录"
    
    # 查看大小
    du -sh $HOME/.ollama
    
    # 移动到数据盘（使用 rsync 更安全）
    rsync -av --progress $HOME/.ollama/ /root/autodl-tmp/ollama/
    
    # 验证迁移成功
    if [ $? -eq 0 ]; then
        echo "✅ 迁移完成"
        
        # 删除原目录（释放系统盘空间）
        rm -rf $HOME/.ollama
        echo "✅ 已删除原目录，释放系统盘空间"
    else
        echo "❌ 迁移失败，保留原文件"
        exit 1
    fi
else
    echo "无现有模型，跳过迁移步骤"
fi
```

**关键改进**:
- ✅ 使用 `rsync` 代替 `cp`，更安全且可显示进度
- ✅ 验证迁移成功后才删除原文件
- ✅ 直接删除原目录（不是改名备份），释放系统盘空间

### 步骤 4: 创建软链接

```bash
# 创建软链接（让 Ollama 认为文件还在原位置）
ln -s /root/autodl-tmp/ollama $HOME/.ollama

# 验证软链接
ls -la $HOME/.ollama
# 输出应该显示: .ollama -> /root/autodl-tmp/ollama

# 验证链接是否有效
readlink -f $HOME/.ollama
# 应该输出: /root/autodl-tmp/ollama
```

### 步骤 5: 设置环境变量（永久生效）

```bash
# 检查是否已经设置
if grep -q "OLLAMA_MODELS" ~/.bashrc; then
    echo "环境变量已存在"
else
    # 添加环境变量
    echo '' >> ~/.bashrc
    echo '# Ollama 数据盘配置' >> ~/.bashrc
    echo 'export OLLAMA_MODELS=/root/autodl-tmp/ollama/models' >> ~/.bashrc
    echo "✅ 环境变量已添加"
fi

# 使配置生效
source ~/.bashrc

# 验证
echo "当前 OLLAMA_MODELS: $OLLAMA_MODELS"
# 应该输出: /root/autodl-tmp/ollama/models
```

### 步骤 6: 启动 Ollama 服务

```bash
# 启动服务（日志输出到数据盘）
nohup ollama serve > /root/autodl-tmp/ollama/logs/ollama.log 2>&1 &

# 记录进程 ID
echo "Ollama PID: $!"

# 等待服务启动
sleep 5

# 验证服务是否正常
if curl -s http://127.0.0.1:11434 > /dev/null; then
    echo "✅ Ollama 服务启动成功"
else
    echo "❌ Ollama 服务启动失败，查看日志:"
    tail -30 /root/autodl-tmp/ollama/logs/ollama.log
    exit 1
fi

# 查看启动日志
tail -20 /root/autodl-tmp/ollama/logs/ollama.log
```

---

## ✅ 验证配置是否成功

### 测试 1: 下载小模型

```bash
# 下载一个小模型测试（约 637MB）
ollama pull tinyllama

# 查看下载位置
ls -lh /root/autodl-tmp/ollama/models/manifests/
ls -lh /root/autodl-tmp/ollama/models/blobs/

# 查看数据盘使用
du -sh /root/autodl-tmp/ollama/
```

### 测试 2: 验证磁盘使用

```bash
# 查看系统盘和数据盘使用情况
df -h / /root/autodl-tmp

# 预期结果:
# 系统盘使用率应该显著降低（如果迁移了大模型）
# 数据盘使用量应该增加
```

### 测试 3: 运行模型

```bash
# 运行刚下载的模型
ollama run tinyllama "你好，请用中文介绍一下你自己"

# 查看模型列表
ollama list
```

### 测试 4: 完整性检查

```bash
# 检查配置
echo "=== 配置检查 ==="
echo "1. 软链接: $(readlink -f ~/.ollama)"
echo "2. 环境变量: $OLLAMA_MODELS"
echo "3. 服务状态: $(curl -s http://127.0.0.1:11434)"
echo "4. 模型位置: $(find /root/autodl-tmp/ollama/models -type f | wc -l) 个文件"
echo "5. 数据盘使用: $(du -sh /root/autodl-tmp/ollama/ | awk '{print $1}')"
```

---

## 🔧 一键迁移脚本

完整的一键迁移脚本（包含所有修正）:

```bash
#!/bin/bash
# 保存为 /root/migrate_ollama_to_datadir.sh

echo "=== Ollama 模型迁移到数据盘 ==="
echo ""

# 1. 停止服务
echo "1. 停止 Ollama 服务..."
pkill ollama
sleep 2

# 2. 创建目录结构
echo "2. 创建数据盘目录..."
mkdir -p /root/autodl-tmp/ollama/models
mkdir -p /root/autodl-tmp/ollama/logs

# 3. 迁移现有模型
if [ -d "$HOME/.ollama" ] && [ ! -L "$HOME/.ollama" ]; then
    echo "3. 发现现有模型，开始迁移..."
    SIZE=$(du -sh $HOME/.ollama | awk '{print $1}')
    echo "   模型大小: $SIZE"
    
    # 使用 rsync 迁移
    rsync -av --progress $HOME/.ollama/ /root/autodl-tmp/ollama/
    
    if [ $? -eq 0 ]; then
        echo "   ✅ 迁移成功"
        
        # 删除原目录释放空间
        rm -rf $HOME/.ollama
        echo "   ✅ 已删除原目录，释放 $SIZE 空间"
    else
        echo "   ❌ 迁移失败"
        exit 1
    fi
else
    echo "3. 无需迁移（无现有模型或已是软链接）"
fi

# 4. 创建软链接
echo "4. 创建软链接..."
ln -sf /root/autodl-tmp/ollama $HOME/.ollama
echo "   ✅ 软链接: ~/.ollama -> /root/autodl-tmp/ollama"

# 5. 设置环境变量
echo "5. 配置环境变量..."
if ! grep -q "OLLAMA_MODELS" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Ollama 数据盘配置
export OLLAMA_MODELS=/root/autodl-tmp/ollama/models
EOF
    echo "   ✅ 环境变量已添加"
else
    echo "   ℹ️  环境变量已存在"
fi

source ~/.bashrc

# 6. 启动服务
echo "6. 启动 Ollama 服务..."
nohup ollama serve > /root/autodl-tmp/ollama/logs/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "   PID: $OLLAMA_PID"

sleep 5

# 7. 验证
echo "7. 验证服务..."
if curl -s http://127.0.0.1:11434 > /dev/null; then
    echo "   ✅ 服务运行正常"
else
    echo "   ❌ 服务启动失败"
    tail -20 /root/autodl-tmp/ollama/logs/ollama.log
    exit 1
fi

echo ""
echo "=== 迁移完成 ==="
echo ""
echo "配置信息:"
echo "  - 模型目录: /root/autodl-tmp/ollama/models"
echo "  - 日志文件: /root/autodl-tmp/ollama/logs/ollama.log"
echo "  - 软链接: ~/.ollama -> /root/autodl-tmp/ollama"
echo "  - 环境变量: OLLAMA_MODELS=$OLLAMA_MODELS"
echo ""
echo "磁盘使用:"
df -h / /root/autodl-tmp
echo ""
echo "下一步:"
echo "  ollama pull tinyllama  # 下载测试模型"
echo "  ollama list            # 查看已有模型"
```

---



















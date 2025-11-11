创建conda环境graphrag后：如果无法激活：

# 1. 初始化 conda for bash
conda init bash

# 2. 重新加载配置
source ~/.bashrc

# 3. 激活环境
conda activate graphrag

安装依赖：
先下载：pip install poetry

安装依赖：
poetry install
    如果下载很慢，安装poetry的镜像源：
        poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
        poetry lock
        poetry install


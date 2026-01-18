# 基于 Python 3.8 镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建默认的输出目录
RUN mkdir -p out/snapshots

# 设置默认命令
CMD ["python", "run_ingram.py", "-i", "targets.txt", "-o", "out"]
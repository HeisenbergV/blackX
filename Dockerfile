FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ src/
COPY strategies/ strategies/
COPY data/ data/

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000 8501

# 设置默认命令
CMD ["bash"] 
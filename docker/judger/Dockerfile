# Docker Judger - 安全的代码执行环境
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk \
    nodejs \
    npm \
    time \
    && rm -rf /var/lib/apt/lists/*

# 创建非特权用户（不指定UID，避免冲突）
RUN useradd -m judger && \
    mkdir -p /sandbox && \
    chown judger:judger /sandbox

# 设置工作目录
WORKDIR /app

# 复制判题脚本
COPY entrypoint.py /app/
COPY limits.conf /etc/security/limits.d/judger.conf

# 设置权限
RUN chmod +x /app/entrypoint.py && \
    chmod 644 /etc/security/limits.d/judger.conf

# 切换到非特权用户
USER judger

# 设置工作目录
WORKDIR /sandbox

# 启动脚本
ENTRYPOINT ["python", "/app/entrypoint.py"]

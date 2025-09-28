#!/bin/bash
# Docker DNS问题快速修复脚本

set -e

echo "🔧 修复Docker DNS问题..."

# 检查Docker状态
if ! systemctl is-active --quiet docker; then
    echo "🔄 启动Docker服务..."
    sudo systemctl start docker
fi

# 备份现有配置
echo "📝 备份现有配置..."
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 配置Docker镜像源
echo "⚙️ 配置Docker镜像源..."
sudo tee /etc/docker/daemon.json > /dev/null <<'DOCKER_CONFIG'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"]
}
DOCKER_CONFIG

# 重启Docker服务
echo "🔄 重启Docker服务..."
sudo systemctl restart docker

# 等待服务启动
sleep 5

# 测试连接
echo "🧪 测试Docker连接..."
if docker pull hello-world > /dev/null 2>&1; then
    echo "✅ Docker连接正常"
    docker rmi hello-world > /dev/null 2>&1 || true
else
    echo "⚠️ Docker连接仍有问题，尝试使用官方源..."
    sudo rm -f /etc/docker/daemon.json
    sudo systemctl restart docker
    sleep 5
fi

# 测试Python镜像
echo "🐍 测试Python镜像..."
if docker pull python:3.11-slim > /dev/null 2>&1; then
    echo "✅ Python镜像下载成功"
    docker rmi python:3.11-slim > /dev/null 2>&1 || true
else
    echo "❌ Python镜像下载失败"
    exit 1
fi

echo "🎉 Docker DNS问题修复完成！"
echo "现在可以重新运行部署脚本："
echo "  ./deploy-linux.sh"

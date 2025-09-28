#!/bin/bash
# Docker镜像源深度修复脚本

set -e

echo "🔧 深度修复Docker镜像源问题..."

# 1. 检查Docker状态
if ! systemctl is-active --quiet docker; then
    echo "🔄 启动Docker服务..."
    sudo systemctl start docker
fi

# 2. 备份现有配置
echo "📝 备份现有配置..."
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 3. 尝试方案1：多镜像源配置
echo "⚙️ 尝试多镜像源配置..."
sudo tee /etc/docker/daemon.json > /dev/null <<'DOCKER_CONFIG'
{
  "registry-mirrors": [
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"],
  "insecure-registries": [],
  "debug": false,
  "experimental": false
}
DOCKER_CONFIG

# 重启Docker服务
sudo systemctl restart docker
sleep 5

# 测试Python镜像
echo "🐍 测试Python镜像（多镜像源）..."
if docker pull python:3.11-slim > /dev/null 2>&1; then
    echo "✅ Python镜像下载成功（多镜像源）"
    docker rmi python:3.11-slim > /dev/null 2>&1 || true
    echo "🎉 Docker镜像源问题修复完成！"
    exit 0
fi

# 4. 尝试方案2：使用官方源
echo "🔄 尝试官方Docker Hub..."
sudo rm -f /etc/docker/daemon.json
sudo systemctl restart docker
sleep 5

echo "🐍 测试Python镜像（官方源）..."
if docker pull python:3.11-slim > /dev/null 2>&1; then
    echo "✅ Python镜像下载成功（官方源）"
    docker rmi python:3.11-slim > /dev/null 2>&1 || true
    echo "🎉 Docker镜像源问题修复完成！"
    exit 0
fi

# 5. 尝试方案3：阿里云镜像源
echo "🔄 尝试阿里云镜像源..."
sudo tee /etc/docker/daemon.json > /dev/null <<'ALIYUN_CONFIG'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"]
}
ALIYUN_CONFIG

sudo systemctl restart docker
sleep 5

echo "🐍 测试Python镜像（阿里云源）..."
if docker pull python:3.11-slim > /dev/null 2>&1; then
    echo "✅ Python镜像下载成功（阿里云源）"
    docker rmi python:3.11-slim > /dev/null 2>&1 || true
    echo "🎉 Docker镜像源问题修复完成！"
    exit 0
fi

# 6. 所有方案都失败
echo "❌ 所有镜像源方案都失败"
echo "🔍 请检查网络连接和防火墙设置"
echo "💡 建议："
echo "   1. 检查网络连接: ping docker.io"
echo "   2. 检查防火墙: sudo ufw status"
echo "   3. 尝试使用代理"
echo "   4. 联系网络管理员"

exit 1

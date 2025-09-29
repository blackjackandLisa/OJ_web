#!/bin/bash
# 部署网络问题修复脚本

set -e

echo "🔧 修复部署网络问题..."

# 1. 检查网络连接
echo "📡 检查网络连接..."
if ! ping -c 3 8.8.8.8 > /dev/null 2>&1; then
    echo "❌ 基本网络连接失败，请检查网络配置"
    exit 1
fi

# 2. 修复DNS配置
echo "🔍 修复DNS配置..."
sudo cp /etc/resolv.conf /etc/resolv.conf.backup 2>/dev/null || true
sudo tee /etc/resolv.conf > /dev/null <<EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 114.114.114.114
nameserver 223.5.5.5
EOF

# 3. 测试DNS解析
echo "🧪 测试DNS解析..."
if nslookup docker.io > /dev/null 2>&1; then
    echo "✅ DNS解析正常"
else
    echo "❌ DNS解析失败"
    exit 1
fi

# 4. 修复Docker配置
echo "🐳 修复Docker配置..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"]
}
EOF

# 5. 重启Docker服务
echo "🔄 重启Docker服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

# 6. 等待Docker启动
sleep 10

# 7. 测试Docker连接
echo "🧪 测试Docker连接..."
if docker pull hello-world > /dev/null 2>&1; then
    echo "✅ Docker连接正常"
    echo "🎉 网络问题修复完成！"
    echo "现在可以重新运行部署脚本："
    echo "  ./deploy-linux.sh"
else
    echo "❌ Docker连接失败"
    echo "💡 建议使用不依赖网络的部署方式："
    echo "  wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-without-git.sh"
    echo "  chmod +x deploy-without-git.sh"
    echo "  ./deploy-without-git.sh"
fi

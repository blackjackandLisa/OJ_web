#!/bin/bash
# 网络连接问题修复脚本

set -e

echo "🔧 修复网络连接问题..."

# 1. 检查网络接口
echo "📡 检查网络接口..."
ip addr show

# 2. 检查路由表
echo "🛣️ 检查路由表..."
ip route show

# 3. 重启网络服务
echo "🔄 重启网络服务..."
sudo systemctl restart networking 2>/dev/null || true
sudo systemctl restart NetworkManager 2>/dev/null || true

# 4. 重新获取IP
echo "🌐 重新获取IP地址..."
sudo dhclient -r 2>/dev/null || true
sudo dhclient 2>/dev/null || true

# 5. 等待网络稳定
sleep 10

# 6. 测试基本连接
echo "🧪 测试基本网络连接..."
if ping -c 3 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ 基本网络连接正常"
else
    echo "❌ 基本网络连接失败"
    echo "💡 请检查网络配置或联系网络管理员"
    exit 1
fi

# 7. 测试DNS解析
echo "🔍 测试DNS解析..."
if nslookup google.com > /dev/null 2>&1; then
    echo "✅ DNS解析正常"
else
    echo "⚠️ DNS解析失败，尝试配置DNS..."
    echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
    echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
    echo "nameserver 114.114.114.114" | sudo tee -a /etc/resolv.conf
fi

# 8. 测试Docker Hub连接
echo "🐳 测试Docker Hub连接..."
if ping -c 3 docker.io > /dev/null 2>&1; then
    echo "✅ Docker Hub连接正常"
    echo "🎉 网络问题修复完成！"
    echo "现在可以重新运行部署脚本："
    echo "  ./deploy-linux.sh"
else
    echo "❌ Docker Hub连接失败"
    echo "💡 建议："
    echo "   1. 检查防火墙设置"
    echo "   2. 检查代理配置"
    echo "   3. 联系网络管理员"
    echo "   4. 使用不依赖网络的部署方式"
fi

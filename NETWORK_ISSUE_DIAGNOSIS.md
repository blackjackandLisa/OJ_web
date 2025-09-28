# 🔍 网络问题深度排查指南

## 🚨 **问题根本原因**

从您的诊断结果看：
- ✅ 防火墙状态：inactive（未启用）
- ❌ 网络连接：100% packet loss to docker.io

**问题确认：**
- 服务器无法访问外网
- 这是网络连接问题，不是Docker配置问题
- 需要解决网络连接才能继续部署

## 🔍 **深度排查步骤**

### **步骤1：检查网络连接状态**

```bash
# 检查网络接口
ip addr show

# 检查路由表
ip route show

# 检查DNS配置
cat /etc/resolv.conf

# 测试基本网络连接
ping -c 3 8.8.8.8
ping -c 3 114.114.114.114
```

### **步骤2：检查网络服务**

```bash
# 检查网络服务状态
sudo systemctl status networking
sudo systemctl status NetworkManager

# 检查网络接口状态
sudo ip link show

# 检查网络配置
sudo cat /etc/netplan/*.yaml
```

### **步骤3：检查DNS解析**

```bash
# 测试DNS解析
nslookup google.com
nslookup docker.io
nslookup registry-1.docker.io

# 检查DNS服务器
dig @8.8.8.8 docker.io
dig @114.114.114.114 docker.io
```

## ✅ **解决方案**

### **方案1：修复网络配置（推荐）**

```bash
# 1. 检查网络接口
ip addr show

# 2. 重启网络服务
sudo systemctl restart networking
sudo systemctl restart NetworkManager

# 3. 重新配置网络
sudo dhclient -r
sudo dhclient

# 4. 测试连接
ping -c 3 8.8.8.8
ping -c 3 docker.io
```

### **方案2：配置静态网络（如果DHCP失败）**

```bash
# 1. 查看当前网络配置
ip route show
ip addr show

# 2. 配置静态IP（需要根据实际情况调整）
sudo tee /etc/netplan/01-netcfg.yaml > /dev/null <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
      dhcp6: false
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4, 114.114.114.114]
EOF

# 3. 应用配置
sudo netplan apply

# 4. 测试连接
ping -c 3 8.8.8.8
```

### **方案3：使用代理（如果有）**

```bash
# 1. 配置系统代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port
export no_proxy=localhost,127.0.0.1

# 2. 配置Docker代理
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<EOF
[Service]
Environment="HTTP_PROXY=http://proxy-server:port"
Environment="HTTPS_PROXY=http://proxy-server:port"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# 3. 重启Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 🚀 **网络修复脚本**

创建一个网络修复脚本：

```bash
# 创建网络修复脚本
cat > fix-network.sh << 'EOF'
#!/bin/bash
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
EOF

# 执行网络修复脚本
chmod +x fix-network.sh
./fix-network.sh
```

## 🎯 **替代部署方案**

如果网络问题无法解决，使用不依赖网络的部署方式：

### **方案A：使用本地Docker镜像**

```bash
# 1. 如果有其他可用的Docker镜像
docker pull ubuntu:20.04
docker tag ubuntu:20.04 python:3.11-slim

# 2. 继续部署
./deploy-linux.sh
```

### **方案B：使用不依赖Docker的部署**

```bash
# 使用不依赖Docker的部署方式
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-without-git.sh
chmod +x deploy-without-git.sh
./deploy-without-git.sh
```

### **方案C：手动部署Django应用**

```bash
# 1. 安装Python和依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装Django
pip install Django

# 4. 创建简单的Django应用
django-admin startproject oj_system
cd oj_system
python manage.py runserver 0.0.0.0:8000
```

## 📞 **联系支持**

如果所有方案都失败，请提供以下信息：

1. **网络配置信息**
   ```bash
   ip addr show
   ip route show
   cat /etc/resolv.conf
   ```

2. **系统信息**
   ```bash
   cat /etc/os-release
   uname -a
   ```

3. **网络测试结果**
   ```bash
   ping -c 3 8.8.8.8
   ping -c 3 docker.io
   ```

## 🎯 **推荐执行步骤**

1. **首先尝试网络修复脚本**
2. **如果失败，尝试方案B**（不依赖Docker部署）
3. **如果仍有问题，使用方案C**（手动部署）

## 💡 **重要提示**

- 网络问题是根本原因，需要先解决网络连接
- 防火墙未启用，不是防火墙问题
- 需要确保服务器可以访问外网
- 如果无法解决网络问题，使用替代部署方案

# 🔧 Docker DNS解析问题解决指南

## 🚨 **当前问题**

您遇到的错误：
```
ERROR: failed to do request: Head "https://docker.mirrors.ustc.edu.cn/v2/library/python/manifests/3.11-slim?ns=docker.io": 
dial tcp: lookup docker.mirrors.ustc.edu.cn on 127.0.0.53:53: no such host
```

**问题原因：**
- Docker镜像源DNS解析失败
- 网络连接问题
- 镜像源配置错误

## ✅ **解决方案**

### **方案1：修复Docker镜像源配置（推荐）**

```bash
# 1. 备份现有配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 2. 配置Docker镜像源
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

# 3. 重启Docker服务
sudo systemctl restart docker

# 4. 验证配置
docker info | grep -A 10 "Registry Mirrors"
```

### **方案2：使用官方Docker Hub**

```bash
# 1. 清除镜像源配置
sudo rm -f /etc/docker/daemon.json

# 2. 重启Docker服务
sudo systemctl restart docker

# 3. 测试连接
docker pull python:3.11-slim
```

### **方案3：修复DNS配置**

```bash
# 1. 检查DNS配置
cat /etc/resolv.conf

# 2. 添加可靠的DNS服务器
sudo tee -a /etc/resolv.conf > /dev/null <<EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 114.114.114.114
EOF

# 3. 测试DNS解析
nslookup docker.mirrors.ustc.edu.cn
nslookup docker.io
```

### **方案4：使用代理（如果有）**

```bash
# 1. 配置Docker代理
sudo mkdir -p /etc/systemd/system/docker.service.d

# 2. 创建代理配置
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<EOF
[Service]
Environment="HTTP_PROXY=http://proxy-server:port"
Environment="HTTPS_PROXY=http://proxy-server:port"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# 3. 重新加载配置
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 🚀 **快速修复脚本**

创建一个一键修复脚本：

```bash
# 创建修复脚本
cat > fix-docker-dns.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 修复Docker DNS问题..."

# 1. 检查Docker状态
if ! systemctl is-active --quiet docker; then
    echo "🔄 启动Docker服务..."
    sudo systemctl start docker
fi

# 2. 备份现有配置
echo "📝 备份现有配置..."
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 3. 配置Docker镜像源
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

# 4. 重启Docker服务
echo "🔄 重启Docker服务..."
sudo systemctl restart docker

# 5. 等待服务启动
sleep 5

# 6. 测试连接
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

# 7. 测试Python镜像
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
EOF

# 执行修复脚本
chmod +x fix-docker-dns.sh
./fix-docker-dns.sh
```

## 🔍 **问题诊断**

### **检查网络连接**
```bash
# 测试DNS解析
nslookup docker.mirrors.ustc.edu.cn
nslookup docker.io

# 测试网络连接
ping -c 3 docker.mirrors.ustc.edu.cn
ping -c 3 docker.io
```

### **检查Docker配置**
```bash
# 查看Docker配置
docker info | grep -A 10 "Registry Mirrors"

# 查看Docker服务状态
sudo systemctl status docker
```

### **检查系统DNS**
```bash
# 查看DNS配置
cat /etc/resolv.conf

# 测试DNS服务器
nslookup google.com
```

## 🎯 **推荐执行步骤**

1. **首先尝试方案1**（修复Docker镜像源配置）
2. **如果失败，尝试方案2**（使用官方Docker Hub）
3. **如果仍有问题，使用快速修复脚本**

## 📝 **修复后重新部署**

```bash
# 修复Docker问题后，重新执行部署
./deploy-linux.sh
```

## 🚨 **如果所有方案都失败**

```bash
# 使用不依赖Docker的部署方式
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-without-git.sh
chmod +x deploy-without-git.sh
./deploy-without-git.sh
```

这个方案会创建一个简化的Django应用，不依赖复杂的Docker构建。

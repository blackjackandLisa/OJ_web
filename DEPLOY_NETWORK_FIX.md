# 🚨 部署网络问题解决方案

## 🔍 **问题分析**

从您的错误信息看，有两个关键问题：

### **问题1：DNS解析失败**
```
dial tcp: lookup docker.mirrors.ustc.edu.cn on 127.0.0.53:53: no such host
```

### **问题2：Docker镜像拉取超时**
```
ERROR: Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection
```

## 🚀 **解决方案**

### **方案1：修复DNS配置（推荐）**

```bash
# 1. 备份现有DNS配置
sudo cp /etc/resolv.conf /etc/resolv.conf.backup

# 2. 配置可靠的DNS服务器
sudo tee /etc/resolv.conf > /dev/null <<EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 114.114.114.114
nameserver 223.5.5.5
EOF

# 3. 测试DNS解析
nslookup docker.io
nslookup registry-1.docker.io
```

### **方案2：修复Docker镜像源配置**

```bash
# 1. 备份现有Docker配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 2. 配置多个镜像源
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
sudo systemctl daemon-reload
sudo systemctl restart docker

# 4. 测试Docker连接
docker pull hello-world
```

### **方案3：使用不依赖网络的部署**

```bash
# 如果网络问题无法解决，使用本地部署
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-without-git.sh
chmod +x deploy-without-git.sh
./deploy-without-git.sh
```

## 🔧 **一键修复脚本**

创建一个综合修复脚本：

```bash
# 创建网络修复脚本
cat > fix-deploy-network.sh << 'EOF'
#!/bin/bash
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
EOF

# 执行修复脚本
chmod +x fix-deploy-network.sh
./fix-deploy-network.sh
```

## 🎯 **推荐执行步骤**

### **步骤1：执行网络修复脚本**
```bash
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/fix-deploy-network.sh
chmod +x fix-deploy-network.sh
./fix-deploy-network.sh
```

### **步骤2：重新运行部署脚本**
```bash
./deploy-linux.sh
```

### **步骤3：如果仍然失败，使用替代方案**
```bash
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-without-git.sh
chmod +x deploy-without-git.sh
./deploy-without-git.sh
```

## 🔍 **手动诊断命令**

如果自动修复失败，可以手动诊断：

```bash
# 1. 检查DNS解析
nslookup docker.io
nslookup registry-1.docker.io

# 2. 检查网络连接
ping -c 3 8.8.8.8
ping -c 3 docker.io

# 3. 检查Docker配置
cat /etc/docker/daemon.json

# 4. 检查Docker服务状态
sudo systemctl status docker

# 5. 测试Docker连接
docker pull hello-world
```

## 💡 **重要提示**

- **DNS问题是主要原因**，需要先解决DNS解析
- **Docker镜像源配置**也很重要
- 如果网络问题无法解决，使用不依赖网络的部署方式
- 建议先尝试自动修复脚本，如果失败再使用替代方案

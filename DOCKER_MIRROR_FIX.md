# 🔧 Docker镜像源问题深度修复

## 🚨 **当前问题分析**

从您的输出看：
- ✅ Docker连接正常
- ❌ Python镜像下载失败

**问题原因：**
- 镜像源配置可能不稳定
- 需要尝试多个镜像源
- 可能需要使用官方源

## ✅ **深度修复方案**

### **方案1：多镜像源配置（推荐）**

```bash
# 1. 配置多个可靠的镜像源
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
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
EOF

# 2. 重启Docker服务
sudo systemctl restart docker

# 3. 测试Python镜像
docker pull python:3.11-slim
```

### **方案2：使用官方Docker Hub**

```bash
# 1. 清除所有镜像源配置，使用官方源
sudo rm -f /etc/docker/daemon.json

# 2. 重启Docker服务
sudo systemctl restart docker

# 3. 测试连接
docker pull python:3.11-slim
```

### **方案3：使用阿里云镜像源**

```bash
# 1. 配置阿里云镜像源
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

# 2. 重启Docker服务
sudo systemctl restart docker

# 3. 测试连接
docker pull python:3.11-slim
```

## 🚀 **增强版修复脚本**

创建一个更强大的修复脚本：

```bash
# 创建增强版修复脚本
cat > fix-docker-mirror.sh << 'EOF'
#!/bin/bash
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
EOF

# 执行增强版修复脚本
chmod +x fix-docker-mirror.sh
./fix-docker-mirror.sh
```

## 🔍 **问题诊断**

### **检查网络连接**
```bash
# 测试Docker Hub连接
ping -c 3 docker.io
ping -c 3 registry-1.docker.io

# 测试镜像源连接
ping -c 3 hub-mirror.c.163.com
ping -c 3 mirror.baidubce.com
```

### **检查Docker配置**
```bash
# 查看当前配置
cat /etc/docker/daemon.json

# 查看Docker信息
docker info | grep -A 10 "Registry Mirrors"
```

### **手动测试镜像源**
```bash
# 测试不同镜像源
docker pull --platform linux/amd64 python:3.11-slim
docker pull python:3.11-alpine
docker pull python:3.11
```

## 🎯 **推荐执行步骤**

1. **首先尝试增强版修复脚本**
2. **如果失败，手动尝试方案2**（官方源）
3. **如果仍有问题，检查网络和防火墙**

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

## 💡 **额外建议**

1. **检查网络环境**：确保服务器可以访问外网
2. **检查防火墙**：确保Docker端口没有被阻止
3. **检查代理设置**：如果有代理，需要配置Docker代理
4. **联系网络管理员**：如果是企业网络，可能需要特殊配置

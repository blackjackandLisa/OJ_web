# 🔧 Linux服务器Git连接问题解决指南

## 🚨 **当前问题**

您遇到了Git TLS连接错误：
```
fatal: unable to access 'https://github.com/blackjackandLisa/OJ_web.git/': 
GnuTLS recv error (-110): The TLS connection was non-properly terminated.
```

## ✅ **解决方案**

### **方案1：修复Git TLS配置（推荐）**

```bash
# 1. 更新Git配置
git config --global http.sslVerify false
git config --global http.postBuffer 1048576000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 2. 重新尝试拉取代码
git pull origin main
```

### **方案2：使用SSH替代HTTPS**

```bash
# 1. 生成SSH密钥（如果没有）
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# 2. 添加SSH密钥到GitHub
cat ~/.ssh/id_rsa.pub
# 复制输出内容到GitHub Settings > SSH and GPG keys

# 3. 更改远程URL为SSH
git remote set-url origin git@github.com:blackjackandLisa/OJ_web.git

# 4. 测试SSH连接
ssh -T git@github.com

# 5. 重新拉取代码
git pull origin main
```

### **方案3：手动下载项目文件**

```bash
# 1. 下载项目压缩包
wget https://github.com/blackjackandLisa/OJ_web/archive/main.zip

# 2. 解压文件
unzip main.zip

# 3. 重命名目录
mv OJ_web-main OJ_web

# 4. 进入项目目录
cd OJ_web

# 5. 继续部署
chmod +x deploy-linux.sh
./deploy-linux.sh
```

### **方案4：使用代理或VPN**

```bash
# 如果在中国大陆，可能需要配置代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port

# 或者使用Git代理
git config --global http.proxy http://proxy-server:port
git config --global https.proxy http://proxy-server:port
```

## 🚀 **快速修复脚本**

创建一个修复脚本：

```bash
# 创建修复脚本
cat > fix-git-connection.sh << 'EOF'
#!/bin/bash
echo "🔧 修复Git连接问题..."

# 方案1: 更新Git配置
echo "📝 更新Git配置..."
git config --global http.sslVerify false
git config --global http.postBuffer 1048576000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 方案2: 尝试重新拉取
echo "🔄 尝试重新拉取代码..."
if git pull origin main; then
    echo "✅ Git拉取成功！"
    exit 0
fi

# 方案3: 手动下载
echo "📥 手动下载项目文件..."
wget -O main.zip https://github.com/blackjackandLisa/OJ_web/archive/main.zip
unzip -o main.zip
mv OJ_web-main OJ_web
cd OJ_web

echo "✅ 项目文件下载完成！"
echo "🚀 现在可以继续部署："
echo "   chmod +x deploy-linux.sh"
echo "   ./deploy-linux.sh"
EOF

# 执行修复脚本
chmod +x fix-git-connection.sh
./fix-git-connection.sh
```

## 🔍 **问题诊断**

### **检查网络连接**
```bash
# 测试GitHub连接
ping github.com

# 测试HTTPS连接
curl -I https://github.com

# 检查DNS解析
nslookup github.com
```

### **检查Git配置**
```bash
# 查看当前Git配置
git config --list

# 查看远程仓库URL
git remote -v
```

### **检查系统时间**
```bash
# TLS错误可能是时间同步问题
date
sudo ntpdate -s time.nist.gov
```

## 🛠️ **替代部署方案**

如果Git问题无法解决，可以使用以下替代方案：

### **方案A：直接使用Docker部署**

```bash
# 1. 创建项目目录
mkdir -p ~/django-oj
cd ~/django-oj

# 2. 手动创建必要文件
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: django_oj
      POSTGRES_USER: oj_user
      POSTGRES_PASSWORD: oj_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
EOF

# 3. 创建Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc g++ default-jdk nodejs npm git curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p media sandbox_tmp judge_temp logs

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

# 4. 创建requirements.txt
cat > requirements.txt << 'EOF'
Django==4.2.24
djangorestframework==3.16.0
django-cors-headers==4.8.0
pillow==10.2.0
psycopg2-binary==2.9.9
redis==5.0.1
django-redis==5.4.0
docker==6.1.3
EOF

# 5. 启动服务
docker-compose up -d
```

### **方案B：使用现有代码**

如果您有项目代码的备份，可以直接上传：

```bash
# 1. 使用scp上传代码（从Windows）
scp -r /path/to/django_OJ_02 username@server-ip:~/django-oj

# 2. 或者使用rsync
rsync -avz /path/to/django_OJ_02/ username@server-ip:~/django-oj/

# 3. 在服务器上继续部署
cd ~/django-oj
chmod +x deploy-linux.sh
./deploy-linux.sh
```

## 📞 **获取帮助**

如果以上方案都无法解决问题，请提供以下信息：

1. **系统信息**
   ```bash
   cat /etc/os-release
   git --version
   curl --version
   ```

2. **网络诊断**
   ```bash
   ping github.com
   curl -I https://github.com
   ```

3. **错误日志**
   ```bash
   git pull origin main 2>&1 | tee git-error.log
   ```

## 🎯 **推荐解决步骤**

1. **首先尝试方案1**（修复Git配置）
2. **如果失败，尝试方案3**（手动下载）
3. **如果仍有问题，使用方案A**（直接Docker部署）

选择最适合您环境的方案，继续完成部署！

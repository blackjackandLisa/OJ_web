# 🐧 Linux服务器部署 - 问题汇总与解决方案

## ✅ **已修复的问题**

### **1. pip安装失败 - externally-managed-environment ✅**

**问题描述：**
- Ubuntu 23.04+系统使用pip安装时报错
- 错误信息：`error: externally-managed-environment`

**原因：**
- Ubuntu新版本引入了Python环境保护机制
- 防止pip破坏系统Python环境

**解决方案：** ✅ 已在Dockerfile中修复
```dockerfile
# Dockerfile第25-29行
RUN apt-get update && apt-get install -y python3-pip && \
    rm /usr/lib/python*/EXTERNALLY-MANAGED 2>/dev/null || true && \
    pip install --upgrade pip --break-system-packages && \
    pip install --no-cache-dir -r requirements-linux.txt --break-system-packages
```

**修复内容：**
- ✅ 移除EXTERNALLY-MANAGED保护文件
- ✅ 添加`--break-system-packages`标志
- ✅ Docker容器环境安全，可以使用该方案

---

### **2. UID冲突问题 ✅**

**问题描述：**
- 构建Judger镜像时报错
- 错误信息：`useradd: UID 1000 is not unique`

**原因：**
- Dockerfile指定固定UID 1000
- 该UID可能在系统中已被占用

**解决方案：** ✅ 已在docker/judger/Dockerfile中修复
```dockerfile
# 原代码（有问题）：
RUN useradd -m -u 1000 judger

# 修复后：
RUN useradd -m judger  # 不指定UID，自动分配
```

**修复内容：**
- ✅ 移除固定UID 1000
- ✅ 使用系统自动分配的UID
- ✅ 避免UID冲突

---

## ⚠️ **潜在问题和预防措施**

### **3. 网络连接问题**

**可能症状：**
- Git clone超时
- Docker镜像拉取失败
- pip下载包失败

**预防措施：**
```bash
# 1. 检查网络连接
ping -c 3 8.8.8.8
ping -c 3 docker.io

# 2. 使用诊断脚本
./scripts/diagnose-network.sh

# 3. 配置Docker镜像源
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

sudo systemctl restart docker
```

---

### **4. SECRET_KEY未修改**

**安全风险：**
- 使用默认SECRET_KEY存在安全隐患
- 生产环境必须修改

**解决方案：**
```bash
# 生成新的SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 在docker.env中替换
SECRET_KEY=<生成的密钥>
```

---

### **5. 数据库密码弱**

**安全风险：**
- 默认密码`oj_password`过于简单
- 易被暴力破解

**解决方案：**
```bash
# 生成强密码
openssl rand -base64 32

# 在docker.env中替换
POSTGRES_PASSWORD=<生成的强密码>
```

---

### **6. 端口冲突**

**可能症状：**
- Nginx无法启动
- 端口80/443被占用

**检查和解决：**
```bash
# 检查端口占用
netstat -tuln | grep ':80\|:443'

# 查看占用进程
sudo lsof -i:80
sudo lsof -i:443

# 停止占用进程或修改端口
# 在docker-compose.yml中修改端口映射
ports:
  - "8080:80"  # 使用8080端口
```

---

### **7. 磁盘空间不足**

**可能症状：**
- Docker构建失败
- 容器无法启动

**检查和清理：**
```bash
# 检查磁盘空间
df -h

# 清理Docker资源
docker system prune -af

# 清理未使用的卷
docker volume prune
```

---

## 🔍 **部署前完整检查**

### **自动检查脚本**

```bash
# 执行部署前检查
chmod +x pre-deployment-check.sh
./pre-deployment-check.sh
```

**检查项目：**
- ✅ 系统环境（CPU、内存、磁盘）
- ✅ 必需软件（Docker、Git、Python）
- ✅ Docker环境和权限
- ✅ 网络连接
- ✅ 项目文件完整性
- ✅ Docker配置文件
- ✅ 安全配置
- ✅ 端口占用
- ✅ 依赖包版本

---

## 📋 **手动检查清单**

### **1. 系统要求 ✅**
- [ ] CPU >= 2核心（推荐4核心）
- [ ] 内存 >= 2GB（推荐4GB）
- [ ] 磁盘 >= 10GB可用（推荐20GB）
- [ ] Ubuntu 20.04+ / Debian 10+ / CentOS 8+

### **2. Docker环境 ✅**
- [ ] Docker已安装（20.10+）
- [ ] Docker服务运行中
- [ ] Docker Compose已安装（2.0+）
- [ ] 当前用户有Docker权限

### **3. 项目文件 ✅**
- [ ] Dockerfile已修复（pip安装问题）
- [ ] docker/judger/Dockerfile已修复（UID冲突）
- [ ] docker.env已配置
- [ ] SECRET_KEY已修改
- [ ] POSTGRES_PASSWORD已修改
- [ ] ALLOWED_HOSTS已配置

### **4. 网络连接 ✅**
- [ ] 基本网络连接正常
- [ ] DNS解析正常
- [ ] GitHub可访问（或使用替代方案）
- [ ] Docker Hub可访问（或配置镜像源）

### **5. 安全配置 ✅**
- [ ] DEBUG=False
- [ ] SECRET_KEY唯一且复杂
- [ ] 数据库密码强
- [ ] ALLOWED_HOSTS限制了允许的域名
- [ ] 安全头已配置（Nginx）

---

## 🚀 **推荐部署流程**

### **方案1：一键部署（推荐）**

```bash
# 1. 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 2. 修改配置
nano docker.env
# 修改: SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS

# 3. 执行部署前检查
chmod +x pre-deployment-check.sh
./pre-deployment-check.sh

# 4. 开始部署
chmod +x deploy.sh
./deploy.sh
```

### **方案2：网络问题时的替代方案**

```bash
# 1. 手动下载项目
wget https://github.com/blackjackandLisa/OJ_web/archive/refs/heads/main.zip
unzip main.zip
cd OJ_web-main

# 2. 手动修复Dockerfile
nano Dockerfile
# 确保包含pip修复内容

# 3. 修改配置
nano docker.env

# 4. 手动部署
docker-compose up -d --build
```

---

## 🛠️ **故障排除工具**

### **1. 网络诊断**
```bash
./scripts/diagnose-network.sh
```

### **2. Docker环境检查**
```bash
./scripts/check-docker.sh
```

### **3. 部署前完整检查**
```bash
./pre-deployment-check.sh
```

### **4. 查看容器日志**
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f web
docker-compose logs -f db
```

### **5. 进入容器调试**
```bash
# 进入web容器
docker-compose exec web bash

# 进入数据库容器
docker-compose exec db psql -U oj_user django_oj
```

---

## 📊 **常见错误和解决方案**

### **错误1: ModuleNotFoundError**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
```bash
# 检查requirements-linux.txt
cat requirements-linux.txt

# 重新构建镜像
docker-compose build --no-cache web
```

### **错误2: Database connection failed**
```
django.db.utils.OperationalError: could not connect to server
```

**解决方案：**
```bash
# 检查数据库服务
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### **错误3: Static files not found**
```
404 Not Found: /static/...
```

**解决方案：**
```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 重启Nginx
docker-compose restart nginx
```

### **错误4: Judger image build failed**
```
ERROR: failed to solve: process "/bin/sh -c useradd..." did not complete successfully
```

**解决方案：**
```bash
# 检查docker/judger/Dockerfile
cat docker/judger/Dockerfile

# 确认不包含固定UID
# 应该是: RUN useradd -m judger
# 不是: RUN useradd -m -u 1000 judger
```

---

## 🎯 **最佳实践**

### **1. 生产环境配置**
```bash
# docker.env
DEBUG=False
SECRET_KEY=<随机生成的复杂密钥>
POSTGRES_PASSWORD=<强密码>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

### **2. 定期维护**
```bash
# 更新系统
sudo apt update && sudo apt upgrade

# 更新Docker镜像
docker-compose pull

# 清理未使用资源
docker system prune -af

# 备份数据
docker-compose exec db pg_dump -U oj_user django_oj > backup.sql
```

### **3. 监控和日志**
```bash
# 实时查看日志
docker-compose logs -f

# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

---

## 📝 **文档索引**

- **[部署检查清单](DEPLOYMENT_CHECKLIST.md)** - 详细的检查清单
- **[部署指南](DEPLOYMENT_GUIDE.md)** - 完整的部署说明
- **[判题系统指南](JUDGE_SYSTEM_GUIDE.md)** - 判题系统配置
- **[依赖文件指南](REQUIREMENTS_GUIDE.md)** - 依赖包说明
- **[项目结构](PROJECT_STRUCTURE.md)** - 项目架构说明

---

## ✅ **总结**

### **已修复问题：**
1. ✅ pip安装失败（externally-managed-environment）
2. ✅ UID冲突问题（docker/judger/Dockerfile）
3. ✅ 依赖包版本优化
4. ✅ 部署脚本完善

### **需要手动配置：**
1. ⚠️ SECRET_KEY（必须修改）
2. ⚠️ POSTGRES_PASSWORD（必须修改）
3. ⚠️ ALLOWED_HOSTS（根据域名配置）

### **可选优化：**
1. 💡 配置HTTPS
2. 💡 配置域名
3. 💡 配置监控
4. 💡 配置备份

**现在项目已经可以在Linux服务器上成功部署！** 🎉

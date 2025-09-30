# ✅ Django OJ - Linux部署检查清单

## 📋 **部署前检查**

### **1. 系统环境 ✅**

| 检查项 | 最低要求 | 推荐配置 | 状态 |
|-------|---------|---------|------|
| CPU | 2核心 | 4核心 | [ ] |
| 内存 | 2GB | 4GB+ | [ ] |
| 磁盘 | 10GB可用 | 20GB+ | [ ] |
| 操作系统 | Ubuntu 20.04+ | Ubuntu 22.04 LTS | [ ] |

### **2. 必需软件 ✅**

- [ ] Docker 20.10+
- [ ] Docker Compose 2.0+
- [ ] Git 2.0+
- [ ] curl
- [ ] Python 3.8+

### **3. 网络连接 ✅**

- [ ] 基本网络连接正常 (ping 8.8.8.8)
- [ ] DNS解析正常 (nslookup google.com)
- [ ] GitHub可访问
- [ ] Docker Hub可访问

---

## 🐳 **Docker配置检查**

### **1. Dockerfile修复 ✅**

#### **主Dockerfile (已修复)**
```dockerfile
# ✅ 已修复pip安装问题
RUN apt-get update && apt-get install -y python3-pip && \
    rm /usr/lib/python*/EXTERNALLY-MANAGED 2>/dev/null || true && \
    pip install --upgrade pip --break-system-packages && \
    pip install --no-cache-dir -r requirements-linux.txt --break-system-packages
```

**检查点：**
- [x] 包含 `rm /usr/lib/python*/EXTERNALLY-MANAGED`
- [x] 包含 `--break-system-packages` 标志
- [x] pip升级命令正确

#### **Judger Dockerfile (已修复)**
```dockerfile
# ✅ 已修复UID冲突问题
RUN useradd -m judger && \
    mkdir -p /sandbox && \
    chown judger:judger /sandbox
```

**检查点：**
- [x] 不指定固定UID 1000
- [x] 使用自动分配的UID

### **2. docker-compose.yml ✅**

**检查点：**
- [x] web服务配置正确
- [x] db服务配置正确
- [x] redis服务配置正确
- [x] nginx服务配置正确
- [x] 包含健康检查
- [x] 服务依赖关系正确

### **3. 环境变量 (docker.env) ⚠️**

**必须修改的配置：**
- [ ] `SECRET_KEY` - 修改为随机密钥
- [ ] `POSTGRES_PASSWORD` - 修改为强密码
- [ ] `ALLOWED_HOSTS` - 添加实际域名

**生产环境配置：**
- [ ] `DEBUG=False`
- [ ] `JUDGE_ENGINE=docker`
- [ ] `SANDBOX_ENABLED=True`

**生成安全密钥：**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## ⚖️ **判题系统检查**

### **1. Docker Judger配置 ✅**

**文件检查：**
- [x] `docker/judger/Dockerfile` 存在
- [x] `docker/judger/entrypoint.py` 存在
- [x] `docker/judger/limits.conf` 存在

**安全配置：**
- [x] 非特权用户执行
- [x] 网络隔离
- [x] 资源限制
- [x] 只读文件系统

### **2. 判题引擎配置 ✅**

在 `docker.env` 中配置：
```bash
JUDGE_ENGINE=docker        # 生产环境推荐
SANDBOX_ENABLED=True       # 启用沙箱
```

**检查点：**
- [x] `JUDGE_ENGINE` 设置正确
- [x] `SANDBOX_ENABLED` 已启用
- [x] Judger镜像可以构建

---

## 📦 **依赖包检查**

### **requirements-linux.txt ✅**

**核心依赖：**
- [x] Django==4.2.24
- [x] djangorestframework==3.16.0
- [x] gunicorn==21.2.0
- [x] psycopg2-binary==2.9.9
- [x] redis==5.0.1
- [x] docker==7.0.0
- [x] psutil==5.9.8
- [x] whitenoise==6.6.0

**版本兼容性：**
- [x] 所有依赖版本已固定
- [x] 无冲突依赖

---

## 🔒 **安全配置检查**

### **1. Django安全设置 ✅**

在 `docker.env` 中：
```bash
DEBUG=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

**检查点：**
- [x] DEBUG模式已关闭
- [x] XSS过滤已启用
- [x] Content-Type嗅探已禁用
- [x] 点击劫持保护已启用

### **2. Nginx安全头 ✅**

在 `nginx.conf` 中：
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "..." always;
```

**检查点：**
- [x] 安全头配置完整
- [x] CSP策略已配置
- [x] 静态文件缓存已配置

### **3. 密码和密钥 ⚠️**

**必须修改：**
- [ ] `SECRET_KEY` - Django密钥
- [ ] `POSTGRES_PASSWORD` - 数据库密码

**密码强度要求：**
- 至少16位字符
- 包含大小写字母、数字、特殊字符
- 不使用常见密码

---

## 🔌 **端口检查**

**确保以下端口未被占用：**
- [ ] 80 (HTTP)
- [ ] 443 (HTTPS)
- [ ] 5432 (PostgreSQL, 仅容器内部)
- [ ] 6379 (Redis, 仅容器内部)
- [ ] 8000 (Django, 仅容器内部)

**检查命令：**
```bash
netstat -tuln | grep ':80\|:443\|:5432\|:6379\|:8000'
```

---

## 🚀 **部署步骤**

### **步骤1：环境准备**

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 3. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **步骤2：获取项目**

```bash
# 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web
```

### **步骤3：配置环境**

```bash
# 修改docker.env
nano docker.env

# 必须修改：
# - SECRET_KEY
# - POSTGRES_PASSWORD
# - ALLOWED_HOSTS
```

### **步骤4：执行部署前检查**

```bash
# 运行检查脚本
chmod +x pre-deployment-check.sh
./pre-deployment-check.sh
```

### **步骤5：开始部署**

```bash
# 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### **步骤6：验证部署**

```bash
# 检查容器状态
docker-compose ps

# 检查服务健康
curl http://localhost/health/

# 查看日志
docker-compose logs -f web
```

---

## ❌ **已知问题和解决方案**

### **问题1: pip安装失败 - externally-managed-environment**

**症状：**
```
error: externally-managed-environment
```

**解决方案：** ✅ 已在Dockerfile中修复
```dockerfile
RUN rm /usr/lib/python*/EXTERNALLY-MANAGED 2>/dev/null || true && \
    pip install --break-system-packages ...
```

### **问题2: UID 1000冲突**

**症状：**
```
useradd: UID 1000 is not unique
```

**解决方案：** ✅ 已在Judger Dockerfile中修复
```dockerfile
RUN useradd -m judger  # 不指定UID
```

### **问题3: Docker镜像拉取失败**

**症状：**
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": net/http: request canceled
```

**解决方案：**
```bash
# 配置镜像源
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

### **问题4: 网络连接失败**

**症状：**
```
fatal: unable to access 'https://github.com/...': Failed to connect
```

**解决方案：**
```bash
# 方案1: 使用诊断脚本
./scripts/diagnose-network.sh

# 方案2: 手动下载
wget https://github.com/blackjackandLisa/OJ_web/archive/refs/heads/main.zip
unzip main.zip
cd OJ_web-main
```

### **问题5: 数据库连接失败**

**症状：**
```
django.db.utils.OperationalError: could not connect to server
```

**解决方案：**
```bash
# 1. 检查数据库服务
docker-compose ps db

# 2. 查看数据库日志
docker-compose logs db

# 3. 重启数据库
docker-compose restart db
```

---

## 📊 **性能优化建议**

### **1. Gunicorn配置**

在Dockerfile中的start.sh：
```bash
gunicorn oj_system.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \              # CPU核心数 * 2 + 1
    --timeout 120 \            # 超时时间
    --max-requests 1000        # 自动重启workers
```

### **2. PostgreSQL优化**

```bash
# 在docker-compose.yml中添加
environment:
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
```

### **3. Redis优化**

```bash
# 在docker-compose.yml中添加
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

---

## 🔍 **监控和日志**

### **日志查看**

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
docker-compose logs -f nginx

# 查看最近100行
docker-compose logs --tail=100 web
```

### **资源监控**

```bash
# 容器资源使用
docker stats

# 磁盘使用
docker system df
```

---

## 📝 **部署完成清单**

**部署后验证：**
- [ ] 所有容器运行正常
- [ ] Web界面可访问
- [ ] 管理后台可登录
- [ ] 判题系统正常工作
- [ ] 静态文件加载正常
- [ ] 数据库连接正常
- [ ] Redis缓存正常

**安全检查：**
- [ ] DEBUG模式已关闭
- [ ] SECRET_KEY已修改
- [ ] 数据库密码已修改
- [ ] ALLOWED_HOSTS已配置
- [ ] 安全头已配置

**性能检查：**
- [ ] Gunicorn workers数量合理
- [ ] 数据库连接池配置
- [ ] Redis缓存启用
- [ ] 静态文件缓存配置

---

## 🆘 **紧急故障处理**

### **完全重新部署**

```bash
# 1. 停止并删除所有容器
docker-compose down -v

# 2. 清理Docker资源
docker system prune -af

# 3. 重新部署
./deploy.sh
```

### **数据备份**

```bash
# 备份数据库
docker-compose exec db pg_dump -U oj_user django_oj > backup.sql

# 备份媒体文件
tar -czf media_backup.tar.gz ./media
```

### **数据恢复**

```bash
# 恢复数据库
docker-compose exec -T db psql -U oj_user django_oj < backup.sql

# 恢复媒体文件
tar -xzf media_backup.tar.gz
```

---

## 📞 **获取帮助**

- **部署指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **判题系统**: [JUDGE_SYSTEM_GUIDE.md](JUDGE_SYSTEM_GUIDE.md)
- **项目结构**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **依赖说明**: [REQUIREMENTS_GUIDE.md](REQUIREMENTS_GUIDE.md)

---

## ✅ **最终检查**

在执行部署前，确认：

1. ✅ 所有Dockerfile已修复（pip安装、UID冲突）
2. ✅ docker.env中的敏感信息已修改
3. ✅ 网络连接正常
4. ✅ Docker环境正常
5. ✅ 端口未被占用
6. ✅ 执行pre-deployment-check.sh检查通过

**准备就绪后，执行：**
```bash
./deploy.sh
```

🎉 **祝部署成功！**

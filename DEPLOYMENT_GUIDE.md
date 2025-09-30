# 🚀 Django OJ System - 部署指南

## 📋 **目录**

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [Docker部署](#docker部署推荐)
- [本地部署](#本地部署)
- [判题系统配置](#判题系统配置)
- [故障排除](#故障排除)

---

## 系统要求

### **最低配置**
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **操作系统**: Ubuntu 20.04+ / Debian 10+ / CentOS 8+

### **推荐配置**
- **CPU**: 4核心
- **内存**: 8GB RAM
- **磁盘**: 50GB 可用空间
- **操作系统**: Ubuntu 22.04 LTS

### **软件要求**
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+

---

## 快速开始

### **一键部署（推荐）**

```bash
# 1. 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 2. 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

**就这么简单！** 脚本会自动检测环境并选择最佳部署方案。

---

## Docker部署（推荐）

### **步骤1：安装Docker和Docker Compose**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### **步骤2：检查Docker环境**

```bash
# 检查Docker
chmod +x scripts/check-docker.sh
./scripts/check-docker.sh
```

### **步骤3：配置环境变量**

```bash
# 创建环境变量文件
cp docker.env.example docker.env

# 编辑环境变量（可选）
nano docker.env
```

**关键配置项：**
```bash
# 数据库密码（建议修改）
POSTGRES_PASSWORD=your_secure_password

# Django密钥（建议修改）
SECRET_KEY=your_secret_key

# 允许的主机（根据实际情况修改）
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

# 判题引擎（推荐使用docker）
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

### **步骤4：构建Docker Judger镜像**

```bash
# 构建安全判题镜像
chmod +x scripts/build_judger.sh
./scripts/build_judger.sh
```

### **步骤5：启动服务**

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

### **步骤6：初始化数据库**

```bash
# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 创建默认模板
docker-compose exec web python manage.py create_default_templates

# 初始化判题配置
docker-compose exec web python manage.py init_judge_config
```

### **步骤7：访问应用**

- **前端**: http://localhost
- **管理后台**: http://localhost/admin

---

## 本地部署

### **步骤1：安装Python环境**

```bash
# 安装Python 3.11
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip
```

### **步骤2：创建虚拟环境**

```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### **步骤3：安装依赖**

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（用于判题）
sudo apt-get install -y gcc g++ default-jdk nodejs npm
```

### **步骤4：配置数据库**

```bash
# 使用SQLite（默认，适合开发）
# 无需额外配置

# 或使用PostgreSQL（推荐生产环境）
sudo apt-get install -y postgresql postgresql-contrib
sudo -u postgres createdb django_oj
sudo -u postgres createuser oj_user -P
```

### **步骤5：运行迁移**

```bash
# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 创建默认模板
python manage.py create_default_templates

# 初始化判题配置
python manage.py init_judge_config
```

### **步骤6：收集静态文件**

```bash
python manage.py collectstatic --noinput
```

### **步骤7：启动服务**

```bash
# 开发环境
python manage.py runserver 0.0.0.0:8000

# 生产环境（使用Gunicorn）
gunicorn oj_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 判题系统配置

### **判题引擎类型**

项目支持三种判题引擎：

#### **1. Docker引擎（推荐生产环境）**

**特点：**
- ✅ 完全容器隔离
- ✅ 最高安全性
- ✅ 资源限制完善
- ✅ 支持所有语言

**配置：**
```bash
# 在docker.env中设置
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

**构建Judger镜像：**
```bash
python manage.py build_judger
```

#### **2. 沙箱引擎（推荐Linux开发环境）**

**特点：**
- ✅ 进程级隔离
- ✅ 良好的安全性
- ✅ 资源限制
- ⚠️ 仅Linux系统

**配置：**
```bash
JUDGE_ENGINE=sandbox
SANDBOX_ENABLED=True
```

#### **3. 基础引擎（仅开发测试）**

**特点：**
- ⚠️ 无安全隔离
- ⚠️ 仅供测试
- ✅ 跨平台支持

**配置：**
```bash
JUDGE_ENGINE=basic
SANDBOX_ENABLED=False
```

### **支持的编程语言**

- **Python** 3.x
- **C++** (g++)
- **C** (gcc)
- **Java** (JDK 11+)
- **JavaScript** (Node.js)

### **资源限制配置**

在Django管理后台可以配置每种语言的资源限制：

- **时间限制**: 默认1-10秒
- **内存限制**: 默认64-256MB
- **文件大小限制**: 默认1MB

---

## 故障排除

### **问题1：Docker镜像拉取失败**

**解决方案：**
```bash
# 诊断网络问题
chmod +x scripts/diagnose-network.sh
./scripts/diagnose-network.sh
```

### **问题2：判题容器构建失败**

**解决方案：**
```bash
# 检查Dockerfile
cat docker/judger/Dockerfile

# 手动构建
cd docker/judger
docker build -t django-oj-judger:latest .
```

### **问题3：数据库连接失败**

**解决方案：**
```bash
# 检查数据库服务
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### **问题4：静态文件无法加载**

**解决方案：**
```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 检查Nginx配置
docker-compose logs nginx
```

### **问题5：判题任务不执行**

**解决方案：**
```bash
# 检查判题引擎配置
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.JUDGE_ENGINE)

# 检查Judger镜像
docker images | grep judger

# 重新构建Judger
python manage.py build_judger
```

### **获取帮助**

- 查看日志: `docker-compose logs -f`
- 进入容器: `docker-compose exec web bash`
- 检查环境: `./scripts/check-docker.sh`
- 诊断网络: `./scripts/diagnose-network.sh`

---

## 常用命令

### **Docker Compose命令**

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

# 进入容器
docker-compose exec web bash

# 清理资源
docker-compose down -v
```

### **Django管理命令**

```bash
# 创建迁移
docker-compose exec web python manage.py makemigrations

# 应用迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic

# 初始化判题配置
docker-compose exec web python manage.py init_judge_config

# 构建判题镜像
docker-compose exec web python manage.py build_judger
```

---

## 生产环境优化

### **1. 使用Nginx反向代理**

已包含在`docker-compose.yml`中，默认监听80端口。

### **2. 配置HTTPS**

```bash
# 安装Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com
```

### **3. 性能优化**

```bash
# 增加Gunicorn workers
# 在docker.env中设置
GUNICORN_WORKERS=4

# 配置Redis缓存
REDIS_URL=redis://redis:6379/1
```

### **4. 日志管理**

```bash
# 配置日志级别
LOG_LEVEL=INFO

# 查看日志
docker-compose logs -f web
```

---

## 安全建议

1. **修改默认密码**: 修改数据库和Django密钥
2. **启用HTTPS**: 使用SSL证书
3. **配置防火墙**: 只开放必要端口
4. **定期备份**: 备份数据库和用户数据
5. **更新依赖**: 定期更新软件包
6. **使用Docker沙箱**: 生产环境必须使用Docker判题引擎

---

## 更新系统

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 运行迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 许可证

MIT License

## 支持

如有问题，请提交Issue或联系开发者。
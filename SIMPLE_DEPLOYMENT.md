# 🚀 Django OJ - 超级简化部署指南

## ✨ **特点**

- ⚡ **超级简单** - 只需3个命令即可部署
- 🐘 **PostgreSQL数据库** - 稳定可靠
- 🛡️ **进程沙箱判题** - 安全且轻量
- 📦 **Docker一键部署** - 无需复杂配置

---

## 📋 **系统要求**

### **最低配置**
- CPU: 1核心
- 内存: 1GB
- 磁盘: 5GB
- 系统: Ubuntu 20.04+ / Debian 10+ / CentOS 8+

### **必需软件**
- Docker 20.10+
- Docker Compose 1.29+

---

## 🚀 **快速部署（3步完成）**

### **步骤1：安装Docker**

```bash
# 一键安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### **步骤2：获取项目**

```bash
# 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 或者手动下载
wget https://github.com/blackjackandLisa/OJ_web/archive/refs/heads/main.zip
unzip main.zip
cd OJ_web-main
```

### **步骤3：一键部署**

```bash
# 执行部署脚本
chmod +x deploy-simple.sh
./deploy-simple.sh
```

**就这么简单！** 🎉

---

## ⚙️ **配置说明**

### **必须修改的配置（docker.env）**

```bash
# 1. 生成SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. 编辑配置文件
nano docker.env

# 3. 修改以下内容：
SECRET_KEY=<刚才生成的密钥>
POSTGRES_PASSWORD=<设置一个强密码>
ALLOWED_HOSTS=<你的服务器IP>,localhost,127.0.0.1
```

### **可选配置**

```bash
# 调试模式（仅开发环境）
DEBUG=True

# 日志级别
LOG_LEVEL=INFO  # 可选: DEBUG, INFO, WARNING, ERROR
```

---

## 📊 **架构说明**

### **服务组成**

```
┌─────────────────────────────────┐
│  Django Web Application         │
│  - 运行在端口 8000              │
│  - Gunicorn WSGI服务器          │
│  - 进程沙箱判题                 │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│  PostgreSQL Database            │
│  - 数据持久化                   │
│  - 自动健康检查                 │
└─────────────────────────────────┘
```

### **判题系统**

- **引擎类型**: 进程沙箱（Sandbox Engine）
- **安全特性**: 
  - ✅ 资源限制（CPU、内存、时间）
  - ✅ 进程隔离
  - ✅ 超时控制
- **支持语言**: Python, C++, C, Java, JavaScript

---

## 📝 **常用操作**

### **查看服务状态**

```bash
docker-compose ps
```

### **查看日志**

```bash
# 查看所有日志
docker-compose logs -f

# 只看web服务
docker-compose logs -f web

# 只看数据库
docker-compose logs -f db
```

### **重启服务**

```bash
# 重启所有服务
docker-compose restart

# 只重启web
docker-compose restart web
```

### **停止服务**

```bash
docker-compose down
```

### **完全清理（包括数据）**

```bash
docker-compose down -v
```

### **进入容器**

```bash
# 进入web容器
docker-compose exec web bash

# 进入数据库
docker-compose exec db psql -U oj_user django_oj
```

---

## 🔧 **Django管理命令**

### **创建管理员**

```bash
docker-compose exec web python manage.py createsuperuser
```

### **数据库迁移**

```bash
docker-compose exec web python manage.py migrate
```

### **收集静态文件**

```bash
docker-compose exec web python manage.py collectstatic
```

### **初始化判题配置**

```bash
docker-compose exec web python manage.py init_judge_config
```

---

## 🌐 **访问应用**

### **本地访问**

- Web界面: http://localhost:8000
- 管理后台: http://localhost:8000/admin

### **远程访问**

- 替换localhost为服务器IP
- 例如: http://192.168.1.100:8000

---

## 🔒 **安全配置**

### **生产环境检查清单**

- [ ] 修改SECRET_KEY为随机值
- [ ] 修改数据库密码
- [ ] 设置DEBUG=False
- [ ] 配置ALLOWED_HOSTS为实际域名/IP
- [ ] 定期备份数据库

### **备份数据**

```bash
# 备份数据库
docker-compose exec db pg_dump -U oj_user django_oj > backup.sql

# 备份媒体文件
tar -czf media_backup.tar.gz ./media
```

### **恢复数据**

```bash
# 恢复数据库
docker-compose exec -T db psql -U oj_user django_oj < backup.sql

# 恢复媒体文件
tar -xzf media_backup.tar.gz
```

---

## ❓ **常见问题**

### **Q1: 端口8000被占用**

```bash
# 查看占用进程
sudo lsof -i:8000

# 修改docker-compose.yml中的端口
ports:
  - "8080:8000"  # 改用8080端口
```

### **Q2: 数据库连接失败**

```bash
# 检查数据库状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### **Q3: 判题不工作**

```bash
# 检查判题引擎配置
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.JUDGE_ENGINE)
sandbox  # 应该输出这个

# 检查judge目录权限
docker-compose exec web ls -la /app/judge_temp
```

### **Q4: 静态文件404**

```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 检查静态文件目录
docker-compose exec web ls -la /app/staticfiles
```

---

## 🔄 **更新系统**

```bash
# 1. 停止服务
docker-compose down

# 2. 拉取最新代码
git pull origin main

# 3. 重新部署
./deploy-simple.sh
```

---

## 📊 **性能优化**

### **低内存服务器（<2GB）**

在docker.env中设置：
```bash
JUDGE_ENGINE=sandbox  # 已默认配置
LOG_LEVEL=WARNING     # 减少日志
```

### **多用户高并发**

修改Dockerfile中的Gunicorn workers：
```bash
--workers 4  # 根据CPU核心数调整
```

---

## 📞 **获取帮助**

- **部署问题**: 查看 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **判题系统**: 查看 [JUDGE_SYSTEM_GUIDE.md](JUDGE_SYSTEM_GUIDE.md)
- **项目结构**: 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## ✅ **部署验证**

部署完成后，验证以下内容：

- [ ] Web界面可访问
- [ ] 管理后台可登录
- [ ] 可以创建题目
- [ ] 可以提交代码
- [ ] 判题功能正常
- [ ] 静态文件加载正常

---

## 🎉 **恭喜！**

您已成功部署Django OJ系统！

**超级简单的部署方案：**
- ✅ 只需2个Docker容器（Web + PostgreSQL）
- ✅ 使用进程沙箱判题（轻量安全）
- ✅ 一键部署脚本
- ✅ 最小化配置

**现在可以开始使用了！** 🚀

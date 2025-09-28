# 🪟 Windows到Linux部署指南

## 📋 **部署概述**

本指南将帮助您将Django OJ系统从Windows开发环境部署到Linux生产服务器。

## 🎯 **部署方式选择**

### **方式1: 一键自动部署（推荐）**

**适用场景：** 快速部署，适合新手

```bash
# 在Linux服务器上执行
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-linux.sh
chmod +x deploy-linux.sh
./deploy-linux.sh
```

### **方式2: 手动部署（推荐）**

**适用场景：** 需要自定义配置，适合有经验的用户

## 🚀 **手动部署步骤**

### **步骤1: 准备Linux服务器**

**服务器要求：**
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- 内存: 2GB+ (推荐4GB+)
- 存储: 20GB+ 可用空间
- 网络: 公网IP（可选）

**连接服务器：**
```bash
# 使用SSH连接
ssh username@your-server-ip

# 或使用云服务器控制台
```

### **步骤2: 安装必需软件**

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install -y curl git wget unzip python3 python3-pip

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

### **步骤3: 获取项目代码**

```bash
# 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 检查项目结构
ls -la
```

### **步骤4: 配置环境变量**

```bash
# 生成安全的SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 编辑环境变量文件
nano docker.env
```

**配置内容：**
```bash
# 数据库配置
DATABASE_URL=postgresql://oj_user:your-strong-password@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=your-strong-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/1

# Django配置
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip,localhost,127.0.0.1

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# 静态文件配置
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 日志配置
LOG_LEVEL=INFO

# 判题系统配置
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
```

### **步骤5: 构建安全判题镜像**

```bash
# 安装Python依赖
pip3 install Django psycopg2-binary docker

# 构建Docker Judger镜像
python3 manage.py build_judger

# 或手动构建
docker build -t django-oj-judger:latest ./docker/judger/
```

### **步骤6: 启动服务**

```bash
# 创建必要目录
mkdir -p media sandbox_tmp judge_temp logs
chmod -R 755 media sandbox_tmp judge_temp logs

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### **步骤7: 初始化数据库**

```bash
# 等待数据库启动
sleep 30

# 执行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 创建默认模板
docker-compose exec web python manage.py create_default_templates

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

### **步骤8: 验证部署**

```bash
# 检查服务健康状态
curl http://localhost/health/

# 检查应用访问
curl http://localhost/

# 查看服务日志
docker-compose logs -f web
```

## 🔧 **高级配置**

### **1. 配置域名和SSL**

```bash
# 安装Nginx
sudo apt install nginx

# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 配置域名解析（在域名提供商处）
# A记录: your-domain.com -> your-server-ip

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

### **2. 配置防火墙**

```bash
# 安装UFW防火墙
sudo apt install ufw

# 配置防火墙规则
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw deny 5432    # 禁止外部访问PostgreSQL
sudo ufw deny 6379    # 禁止外部访问Redis

# 启用防火墙
sudo ufw enable
```

### **3. 配置自动备份**

```bash
# 创建备份脚本
sudo nano /usr/local/bin/backup-oj.sh
```

**备份脚本内容：**
```bash
#!/bin/bash
BACKUP_DIR="/backup/oj"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T db pg_dump -U oj_user django_oj > $BACKUP_DIR/db_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

```bash
# 设置执行权限
sudo chmod +x /usr/local/bin/backup-oj.sh

# 设置定时任务
sudo crontab -e
```

**添加定时任务：**
```bash
# 每天凌晨2点备份
0 2 * * * /usr/local/bin/backup-oj.sh
```

## 📊 **监控和维护**

### **服务监控**

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

### **性能优化**

```bash
# 调整Docker资源限制
nano docker-compose.yml
```

**优化配置示例：**
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🚨 **故障排除**

### **常见问题**

1. **服务启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs web
   
   # 重启服务
   docker-compose restart
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose exec db pg_isready -U oj_user -d django_oj
   
   # 重启数据库
   docker-compose restart db
   ```

3. **静态文件404**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **判题系统问题**
   ```bash
   # 测试判题引擎
   docker-compose exec web python scripts/test_judge_security.py
   
   # 重建judger镜像
   docker-compose exec web python manage.py build_judger
   ```

## 🔄 **更新和维护**

### **更新应用**

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 执行数据库迁移
docker-compose exec web python manage.py migrate
```

### **备份和恢复**

```bash
# 备份数据
./backup-oj.sh

# 恢复数据库
docker-compose exec -T db psql -U oj_user django_oj < backup/db_20240101_120000.sql

# 恢复媒体文件
tar -xzf backup/media_20240101_120000.tar.gz
```

## 📝 **部署检查清单**

### **部署前检查**
- [ ] Linux服务器已准备就绪
- [ ] Docker和Docker Compose已安装
- [ ] 项目代码已克隆
- [ ] 环境变量已配置
- [ ] 防火墙规则已设置

### **部署后检查**
- [ ] 所有服务正常运行
- [ ] 数据库连接正常
- [ ] 静态文件加载正常
- [ ] 判题系统工作正常
- [ ] SSL证书配置正确（如适用）
- [ ] 备份策略已设置

## 🎯 **快速部署命令**

```bash
# 一键部署（推荐）
wget https://raw.githubusercontent.com/blackjackandLisa/OJ_web/main/deploy-linux.sh
chmod +x deploy-linux.sh
./deploy-linux.sh
```

## 🎉 **部署完成**

恭喜！您的Django OJ系统已成功部署到Linux服务器。

**访问地址：**
- 主应用: `http://your-server-ip`
- 管理界面: `http://your-server-ip/admin`
- 健康检查: `http://your-server-ip/health/`

**管理命令：**
```bash
# 查看服务状态
docker-compose ps

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

您的在线判题系统现在已经完全部署并运行在Linux服务器上！🚀

# 🐧 Linux服务器部署操作指南

## 📋 **部署前准备**

### **1. 服务器要求**
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **内存**: 最少 2GB，推荐 4GB+
- **存储**: 最少 20GB 可用空间
- **网络**: 公网IP（可选，用于域名访问）

### **2. 必需软件**
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

## 🚀 **部署步骤**

### **步骤1: 服务器环境准备**

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必需软件
sudo apt install -y curl git wget unzip

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录以应用组权限
exit
```

### **步骤2: 获取项目代码**

```bash
# 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 检查项目结构
ls -la
```

### **步骤3: 配置环境变量**

```bash
# 生成安全的SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 编辑环境变量文件
nano docker.env
```

**配置 `docker.env` 文件：**
```bash
# 数据库配置
DATABASE_URL=postgresql://oj_user:oj_password@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/1

# Django配置
SECRET_KEY=your-generated-secret-key-here
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

### **步骤4: 构建Docker Judger镜像**

```bash
# 构建安全判题镜像
python3 manage.py build_judger

# 或者手动构建
docker build -t django-oj-judger:latest ./docker/judger/
```

### **步骤5: 启动服务**

```bash
# 创建必要目录
mkdir -p media sandbox_tmp judge_temp logs

# 设置权限
chmod -R 755 media sandbox_tmp judge_temp logs

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### **步骤6: 初始化数据库**

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

### **步骤7: 验证部署**

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
# 安装Nginx（如果使用外部Nginx）
sudo apt install nginx

# 安装Certbot
sudo apt install certbot python3-certbot-nginx

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
sudo ufw allow 443     # HTTPS
sudo ufw deny 5432     # 禁止外部访问PostgreSQL
sudo ufw deny 6379     # 禁止外部访问Redis

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

# 创建备份目录
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

### **1. 服务监控**

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

### **2. 性能优化**

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

### **3. 日志管理**

```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/docker-oj
```

**日志轮转配置：**
```
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

## 🚨 **故障排除**

### **常见问题解决**

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

### **性能问题**

1. **内存不足**
   ```bash
   # 查看内存使用
   free -h
   
   # 调整Docker内存限制
   nano docker-compose.yml
   ```

2. **磁盘空间不足**
   ```bash
   # 清理Docker缓存
   docker system prune -a
   
   # 清理旧日志
   docker-compose logs --tail=0 -f
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
- [ ] 服务器配置满足要求
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
# 一键部署脚本
#!/bin/bash
set -e

echo "🚀 开始部署Django OJ系统..."

# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 克隆项目
git clone https://github.com/blackjackandLisa/OJ_web.git
cd OJ_web

# 5. 配置环境变量
cp docker.env.example docker.env
# 编辑 docker.env 文件

# 6. 创建目录
mkdir -p media sandbox_tmp judge_temp logs

# 7. 启动服务
docker-compose up -d

# 8. 初始化数据库
sleep 30
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py create_default_templates
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ 部署完成！"
echo "访问地址: http://your-server-ip"
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

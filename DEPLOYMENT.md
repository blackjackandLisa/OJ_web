# 部署指南

## 🚀 生产环境部署

### 1. 环境准备

#### 系统要求
- Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- Python 3.8+
- Git
- Docker (可选，推荐用于评测系统)

#### 安装Python依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git

# Windows
# 下载并安装Python 3.8+和Git
```

### 2. 项目部署

#### 克隆项目
```bash
git clone https://github.com/yourusername/django-oj-system.git
cd django-oj-system
```

#### 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置数据库
```bash
# 使用PostgreSQL (推荐)
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb django_oj
sudo -u postgres createuser oj_user

# 或使用MySQL
sudo apt install mysql-server
mysql -u root -p
CREATE DATABASE django_oj;
CREATE USER 'oj_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON django_oj.* TO 'oj_user'@'localhost';
```

#### 配置生产环境设置
创建 `local_settings.py`:
```python
# local_settings.py
import os

# 安全设置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# 数据库配置 (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_oj',
        'USER': 'oj_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 密钥配置
SECRET_KEY = 'your-secret-key-here'

# 静态文件配置
STATIC_ROOT = '/var/www/django-oj/static/'
MEDIA_ROOT = '/var/www/django-oj/media/'

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'

# 评测系统配置
JUDGE_ENGINE = 'docker'  # 生产环境推荐使用Docker
JUDGE_DOCKER_IMAGE = 'oj-judger:latest'
```

#### 执行迁移
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_default_templates
python manage.py collectstatic
```

### 3. Web服务器配置

#### 使用Nginx + Gunicorn

安装Gunicorn:
```bash
pip install gunicorn
```

创建Gunicorn配置文件 `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

安装和配置Nginx:
```bash
sudo apt install nginx

# 创建Nginx配置
sudo nano /etc/nginx/sites-available/django-oj
```

Nginx配置示例:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location /static/ {
        alias /var/www/django-oj/static/;
    }
    
    location /media/ {
        alias /var/www/django-oj/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/django-oj /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 系统服务配置

创建systemd服务文件:
```bash
sudo nano /etc/systemd/system/django-oj.service
```

服务配置:
```ini
[Unit]
Description=Django OJ System
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/django-oj-system
Environment=PATH=/path/to/django-oj-system/venv/bin
ExecStart=/path/to/django-oj-system/venv/bin/gunicorn oj_system.wsgi:application -c gunicorn.conf.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-oj
sudo systemctl start django-oj
```

### 5. SSL配置 (可选但推荐)

使用Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 6. 监控和日志

#### 配置日志
在 `settings.py` 中:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django-oj/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### 设置日志轮转
```bash
sudo nano /etc/logrotate.d/django-oj
```

```
/var/log/django-oj/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 7. 性能优化

#### 数据库优化
- 配置数据库连接池
- 添加数据库索引
- 定期数据库维护

#### 缓存配置
安装Redis:
```bash
sudo apt install redis-server
pip install redis django-redis
```

在 `settings.py` 中配置:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 8. 安全检查清单

- [ ] 设置 `DEBUG = False`
- [ ] 配置正确的 `ALLOWED_HOSTS`
- [ ] 使用强密码和密钥
- [ ] 启用HTTPS
- [ ] 配置防火墙
- [ ] 定期更新系统和依赖
- [ ] 配置自动备份
- [ ] 监控系统日志

### 9. 备份策略

创建备份脚本:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/django-oj"

# 数据库备份
pg_dump django_oj > $BACKUP_DIR/db_$DATE.sql

# 媒体文件备份
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/django-oj/media/

# 清理旧备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

设置定时任务:
```bash
crontab -e
# 每天凌晨2点备份
0 2 * * * /path/to/backup-script.sh
```

### 10. 故障排查

#### 常见问题
1. **静态文件无法加载**
   - 检查 `STATIC_ROOT` 配置
   - 运行 `python manage.py collectstatic`
   - 检查Nginx静态文件配置

2. **数据库连接错误**
   - 检查数据库服务状态
   - 验证连接参数
   - 查看数据库日志

3. **评测系统无法工作**
   - 检查Docker服务状态
   - 验证评测目录权限
   - 查看评测日志

#### 日志查看
```bash
# 系统服务日志
sudo journalctl -u django-oj -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 应用日志
tail -f /var/log/django-oj/django.log
```

#!/bin/bash
# 不依赖Git的Linux部署脚本

set -e

echo "🚀 开始部署Django OJ系统（不依赖Git）..."

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要使用root用户运行此脚本"
    echo "请使用普通用户，脚本会自动处理sudo权限"
    exit 1
fi

# 检查操作系统
if ! command -v apt &> /dev/null; then
    echo "❌ 此脚本仅支持基于Debian/Ubuntu的系统"
    echo "请手动按照 LINUX_DEPLOYMENT_GUIDE.md 进行部署"
    exit 1
fi

echo "📋 检查系统环境..."

# 更新系统
echo "🔄 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础软件
echo "📦 安装基础软件..."
sudo apt install -y curl git wget unzip python3 python3-pip

# 安装Docker
echo "🐳 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker安装完成"
else
    echo "✅ Docker已安装"
fi

# 安装Docker Compose
echo "🐳 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "✅ Docker Compose已安装"
fi

# 检查Docker服务
echo "🔍 检查Docker服务..."
if ! sudo systemctl is-active --quiet docker; then
    echo "🔄 启动Docker服务..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 创建项目目录
echo "📁 创建项目目录..."
PROJECT_DIR="$HOME/django-oj"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 创建Docker Compose文件
echo "📝 创建Docker Compose配置..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://oj_user:${DB_PASSWORD}@db:5432/django_oj
      - REDIS_URL=redis://redis:6379/1
      - ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: django_oj
      POSTGRES_USER: oj_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U oj_user -d django_oj"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# 创建Dockerfile
echo "📝 创建Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc g++ default-jdk nodejs npm git curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p media sandbox_tmp judge_temp logs

# 设置权限
RUN chmod -R 755 media sandbox_tmp judge_temp logs

# 启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting Django OJ System..."\n\
\n\
# Wait for database\n\
echo "⏳ Waiting for database..."\n\
while ! python manage.py shell -c "from django.db import connection; connection.ensure_connection()" 2>/dev/null; do\n\
    echo "⏳ Database not ready, waiting 5 seconds..."\n\
    sleep 5\n\
done\n\
echo "✅ Database connected"\n\
\n\
# Run migrations\n\
echo "🔄 Running migrations..."\n\
python manage.py migrate\n\
\n\
# Create default templates\n\
echo "📝 Creating default templates..."\n\
python manage.py create_default_templates\n\
\n\
# Collect static files\n\
echo "📦 Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
# Start Gunicorn\n\
echo "🚀 Starting Gunicorn..."\n\
exec gunicorn oj_system.wsgi:application \\\n\
    --bind 0.0.0.0:8000 \\\n\
    --workers 3 \\\n\
    --timeout 120 \\\n\
    --keep-alive 2 \\\n\
    --max-requests 1000 \\\n\
    --max-requests-jitter 100 \\\n\
    --preload\n\
' > start.sh && chmod +x start.sh

CMD ["./start.sh"]
EOF

# 创建requirements.txt
echo "📝 创建requirements.txt..."
cat > requirements.txt << 'EOF'
Django==4.2.24
djangorestframework==3.16.0
django-cors-headers==4.8.0
pillow==10.2.0
psycopg2-binary==2.9.9
redis==5.0.1
django-redis==5.4.0
docker==6.1.3
gunicorn==21.2.0
EOF

# 创建基础Django项目结构
echo "📝 创建Django项目结构..."
mkdir -p oj_system problems contests submissions accounts judge monitor templates static media

# 创建基础Django文件
cat > manage.py << 'EOF'
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
EOF

# 创建基础settings.py
cat > oj_system/settings.py << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'problems',
    'contests',
    'submissions',
    'accounts',
    'judge',
    'monitor',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oj_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oj_system.wsgi.application'

# Database
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'django_oj',
            'USER': 'oj_user',
            'PASSWORD': os.environ.get('DB_PASSWORD', 'oj_password'),
            'HOST': 'db',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Redis
if os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True
EOF

# 创建基础URLs
cat > oj_system/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('problems.urls')),
    path('contests/', include('contests.urls')),
    path('submissions/', include('submissions.urls')),
    path('accounts/', include('accounts.urls')),
    path('judge/', include('judge.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
EOF

# 创建基础WSGI
cat > oj_system/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_system.settings')
application = get_wsgi_application()
EOF

# 创建基础ASGI
cat > oj_system/asgi.py << 'EOF'
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_system.settings')
application = get_asgi_application()
EOF

# 创建基础__init__.py文件
for app in oj_system problems contests submissions accounts judge monitor; do
    mkdir -p $app
    touch $app/__init__.py
    touch $app/apps.py
    touch $app/models.py
    touch $app/views.py
    touch $app/urls.py
    touch $app/admin.py
    touch $app/serializers.py
    touch $app/tests.py
done

# 创建基础模板
mkdir -p templates
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django OJ System</title>
</head>
<body>
    <h1>Django OJ System</h1>
    <p>系统正在运行中...</p>
</body>
</html>
EOF

# 创建基础problems应用
cat > problems/urls.py << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
]
EOF

cat > problems/views.py << 'EOF'
from django.shortcuts import render
from django.http import HttpResponse

def problem_list(request):
    return HttpResponse("<h1>问题列表</h1><p>Django OJ系统正在运行中...</p>")
EOF

# 配置环境变量
echo "⚙️ 配置环境变量..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
SERVER_IP=$(curl -s ifconfig.me || echo "localhost")

export SECRET_KEY
export DB_PASSWORD
export SERVER_IP

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p media sandbox_tmp judge_temp logs
chmod -R 755 media sandbox_tmp judge_temp logs

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ 服务启动失败，查看日志："
    docker-compose logs
    exit 1
fi

# 显示部署结果
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服务信息："
echo "   - 主应用: http://${SERVER_IP}:8000"
echo "   - 管理界面: http://${SERVER_IP}:8000/admin"
echo ""
echo "🔧 管理命令："
echo "   - 查看服务状态: docker-compose ps"
echo "   - 查看日志: docker-compose logs -f"
echo "   - 重启服务: docker-compose restart"
echo "   - 停止服务: docker-compose down"
echo ""
echo "🔑 重要信息："
echo "   - 数据库密码: ${DB_PASSWORD}"
echo "   - SECRET_KEY: ${SECRET_KEY}"
echo "   - 请妥善保存这些信息！"
echo ""
echo "⚠️ 注意：这是一个简化版本，用于快速部署测试"
echo "   生产环境请使用完整的项目代码"

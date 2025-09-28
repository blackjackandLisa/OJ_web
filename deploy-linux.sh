#!/bin/bash
# Linux服务器一键部署脚本

set -e

echo "🚀 开始部署Django OJ系统到Linux服务器..."

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

# 获取项目代码
echo "📥 获取项目代码..."
if [ ! -d "OJ_web" ]; then
    git clone https://github.com/blackjackandLisa/OJ_web.git
    cd OJ_web
else
    echo "✅ 项目代码已存在，更新中..."
    cd OJ_web
    git pull origin main
fi

# 配置环境变量
echo "⚙️ 配置环境变量..."
if [ ! -f "docker.env" ]; then
    echo "📝 创建环境变量文件..."
    
    # 生成安全的SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # 生成数据库密码
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || echo "localhost")
    
    cat > docker.env << EOF
# 数据库配置
DATABASE_URL=postgresql://oj_user:${DB_PASSWORD}@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/1

# Django配置
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1

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
EOF
    
    echo "✅ 环境变量文件已创建"
    echo "🔑 数据库密码: ${DB_PASSWORD}"
    echo "🔑 SECRET_KEY: ${SECRET_KEY}"
else
    echo "✅ 环境变量文件已存在"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p media sandbox_tmp judge_temp logs
chmod -R 755 media sandbox_tmp judge_temp logs

# 构建Docker Judger镜像
echo "🔨 构建Docker Judger镜像..."
if command -v python3 &> /dev/null; then
    # 安装Django依赖
    pip3 install Django psycopg2-binary docker
    
    # 构建judger镜像
    python3 manage.py build_judger || {
        echo "⚠️ 自动构建失败，手动构建..."
        docker build -t django-oj-judger:latest ./docker/judger/
    }
else
    echo "⚠️ Python3不可用，跳过自动构建"
    docker build -t django-oj-judger:latest ./docker/judger/
fi

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

# 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose exec -T web python manage.py migrate || {
    echo "⚠️ 数据库迁移失败，等待数据库启动..."
    sleep 30
    docker-compose exec -T web python manage.py migrate
}

# 创建默认模板
echo "📝 创建默认模板..."
docker-compose exec -T web python manage.py create_default_templates || echo "⚠️ 模板创建失败，可稍后手动创建"

# 收集静态文件
echo "📦 收集静态文件..."
docker-compose exec -T web python manage.py collectstatic --noinput

# 测试服务
echo "🧪 测试服务..."
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ 服务健康检查通过"
else
    echo "⚠️ 服务健康检查失败，但服务可能仍在启动中"
fi

# 显示部署结果
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服务信息："
echo "   - 主应用: http://${SERVER_IP}"
echo "   - 管理界面: http://${SERVER_IP}/admin"
echo "   - 健康检查: http://${SERVER_IP}/health/"
echo ""
echo "🔧 管理命令："
echo "   - 查看服务状态: docker-compose ps"
echo "   - 查看日志: docker-compose logs -f"
echo "   - 重启服务: docker-compose restart"
echo "   - 停止服务: docker-compose down"
echo ""
echo "👤 创建超级用户："
echo "   docker-compose exec web python manage.py createsuperuser"
echo ""
echo "🔑 重要信息："
echo "   - 数据库密码: ${DB_PASSWORD}"
echo "   - SECRET_KEY: ${SECRET_KEY}"
echo "   - 请妥善保存这些信息！"
echo ""
echo "📖 详细文档: LINUX_DEPLOYMENT_GUIDE.md"
echo ""
echo "⚠️ 安全提醒："
echo "   1. 请修改默认密码"
echo "   2. 配置防火墙规则"
echo "   3. 设置SSL证书（生产环境）"
echo "   4. 配置定期备份"
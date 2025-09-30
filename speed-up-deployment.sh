#!/bin/bash
# 加速部署脚本 - 使用国内镜像源的PostgreSQL

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "Django OJ - 加速部署脚本"
echo "使用国内镜像源，大幅提升下载速度"
echo "=========================================="

# 停止并清理旧容器
log_info "停止旧容器..."
docker-compose down 2>/dev/null || true

# 使用国内公开镜像源拉取PostgreSQL
log_info "🚀 使用国内镜像源拉取PostgreSQL（速度更快）..."

# 尝试多个镜像源，找到可用的
if docker pull docker.1panel.live/library/postgres:15-alpine 2>/dev/null; then
    log_info "使用1Panel镜像源"
    docker tag docker.1panel.live/library/postgres:15-alpine postgres:15-alpine
elif docker pull docker.m.daocloud.io/library/postgres:15-alpine 2>/dev/null; then
    log_info "使用DaoCloud镜像源"
    docker tag docker.m.daocloud.io/library/postgres:15-alpine postgres:15-alpine
elif docker pull mirror.ccs.tencentyun.com/library/postgres:15-alpine 2>/dev/null; then
    log_info "使用腾讯云镜像源"
    docker tag mirror.ccs.tencentyun.com/library/postgres:15-alpine postgres:15-alpine
else
    log_warning "国内镜像源不可用，使用Docker Hub（可能较慢）"
    docker pull postgres:15-alpine
fi

log_success "✅ PostgreSQL镜像准备完成！"

# 拉取Python镜像（如果需要）
log_info "🚀 拉取Python镜像..."
docker pull python:3.11-slim 2>/dev/null || log_warning "Python镜像将在构建时下载"

log_success "✅ 所有镜像准备完成！"

# 检查docker.env
if [ ! -f "docker.env" ]; then
    log_warning "⚠️  未找到docker.env文件"
    log_info "创建默认配置文件..."
    cat > docker.env <<'EOF'
# Django配置
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 数据库配置
DATABASE_URL=postgresql://oj_user:oj_password@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=oj_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# 安全配置
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# 静态文件配置
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 日志配置
LOG_LEVEL=INFO

# 判题系统配置（简化版本）
JUDGE_ENGINE=sandbox
SANDBOX_ENABLED=True
EOF
    log_warning "⚠️  请修改docker.env中的SECRET_KEY和POSTGRES_PASSWORD！"
    echo ""
    log_info "生成随机SECRET_KEY："
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "请手动生成SECRET_KEY"
    echo ""
    read -p "按回车继续部署，或按Ctrl+C退出修改配置..."
fi

# 启动服务
log_info "🚀 启动Docker Compose服务..."
docker-compose up -d --build

log_success "✅ 服务启动中..."

# 等待数据库就绪
log_info "等待数据库启动..."
sleep 10

# 检查服务状态
log_info "检查服务状态..."
docker-compose ps

echo ""
log_success "=========================================="
log_success "🎉 部署完成！"
log_success "=========================================="
echo ""
log_info "访问地址："
echo -e "  ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
log_info "管理后台："
echo -e "  ${GREEN}http://$(hostname -I | awk '{print $1}'):8000/admin${NC}"
echo ""
log_info "查看日志："
echo -e "  ${YELLOW}docker-compose logs -f web${NC}"
echo ""
log_info "创建管理员账号："
echo -e "  ${YELLOW}docker-compose exec web python manage.py createsuperuser${NC}"
echo ""

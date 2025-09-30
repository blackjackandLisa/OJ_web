#!/bin/bash
# Django OJ System - 超级简化部署脚本
# 适用于快速部署，只需Docker和Docker Compose

set -e

echo "=========================================="
echo "   Django OJ - 简化部署脚本"
echo "=========================================="
echo ""

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 检查Docker
log_info "检查Docker环境..."
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    echo "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose未安装"
    echo "安装命令: sudo apt-get install docker-compose"
    exit 1
fi

log_success "Docker环境检查通过"

# 2. 检查配置文件
log_info "检查配置文件..."
if [ ! -f "docker.env" ]; then
    log_error "docker.env文件不存在"
    exit 1
fi

# 检查是否修改了默认密钥
if grep -q "your-secret-key-here" docker.env; then
    log_info "⚠️  建议修改docker.env中的SECRET_KEY"
    echo "生成命令: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
fi

# 3. 停止旧容器
log_info "停止旧容器..."
docker-compose down 2>/dev/null || true

# 4. 构建并启动
log_info "构建并启动服务..."
docker-compose up -d --build

# 5. 等待服务启动
log_info "等待服务启动..."
sleep 10

# 6. 检查服务状态
log_info "检查服务状态..."
docker-compose ps

# 7. 初始化数据库
log_info "初始化数据库..."
docker-compose exec -T web python manage.py migrate

# 8. 创建默认模板
log_info "创建默认代码模板..."
docker-compose exec -T web python manage.py create_default_templates 2>/dev/null || true

# 9. 收集静态文件
log_info "收集静态文件..."
docker-compose exec -T web python manage.py collectstatic --noinput

# 10. 创建管理员账号（可选）
echo ""
log_info "是否创建管理员账号？(y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

# 完成
echo ""
echo "=========================================="
log_success "部署完成！"
echo "=========================================="
echo ""
echo "📊 服务信息："
echo "  - Web访问地址: http://localhost:8000"
echo "  - 管理后台: http://localhost:8000/admin"
echo ""
echo "📝 常用命令："
echo "  - 查看日志: docker-compose logs -f web"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""

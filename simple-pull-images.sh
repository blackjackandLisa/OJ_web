#!/bin/bash
# 简单镜像拉取脚本 - 无需登录，使用公开镜像源

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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "Django OJ - 镜像拉取脚本"
echo "尝试多个镜像源，无需登录"
echo "=========================================="

# 清理旧容器
log_info "清理旧容器..."
docker-compose down 2>/dev/null || true

# 定义多个镜像源
log_info "开始拉取PostgreSQL镜像..."

# 尝试1: Docker Hub官方（已经配置了加速）
log_info "尝试方式1: 使用已配置的Docker镜像加速..."
if docker pull postgres:15-alpine; then
    log_success "✅ 使用Docker Hub拉取成功！"
else
    log_error "❌ 方式1失败，尝试方式2..."
    
    # 尝试2: 使用Docker Proxy
    log_info "尝试方式2: 使用Docker Proxy..."
    if docker pull docker.1panel.live/library/postgres:15-alpine; then
        docker tag docker.1panel.live/library/postgres:15-alpine postgres:15-alpine
        log_success "✅ 使用1Panel镜像成功！"
    else
        log_error "❌ 方式2失败，尝试方式3..."
        
        # 尝试3: 使用DaoCloud
        log_info "尝试方式3: 使用DaoCloud镜像..."
        if docker pull docker.m.daocloud.io/library/postgres:15-alpine; then
            docker tag docker.m.daocloud.io/library/postgres:15-alpine postgres:15-alpine
            log_success "✅ 使用DaoCloud镜像成功！"
        else
            log_error "❌ 方式3失败，尝试方式4..."
            
            # 尝试4: 使用腾讯云镜像
            log_info "尝试方式4: 使用腾讯云镜像..."
            if docker pull mirror.ccs.tencentyun.com/library/postgres:15-alpine; then
                docker tag mirror.ccs.tencentyun.com/library/postgres:15-alpine postgres:15-alpine
                log_success "✅ 使用腾讯云镜像成功！"
            else
                log_error "❌ 所有镜像源都失败"
                log_info "建议："
                echo "  1. 检查网络连接"
                echo "  2. 检查防火墙设置"
                echo "  3. 等待几分钟后重试"
                echo "  4. 或者让原来的下载继续（虽然慢）"
                exit 1
            fi
        fi
    fi
fi

log_success "✅ PostgreSQL镜像准备完成！"

# 拉取Python镜像
log_info "拉取Python镜像..."
docker pull python:3.11-slim || log_error "Python镜像拉取失败，构建时会重试"

# 显示已有镜像
log_info "当前已有镜像："
docker images | grep -E "postgres|python"

echo ""
log_success "✅ 镜像准备完成！现在可以部署了！"
echo ""
log_info "执行部署："
echo -e "  ${GREEN}./deploy-simple.sh${NC}"
echo ""

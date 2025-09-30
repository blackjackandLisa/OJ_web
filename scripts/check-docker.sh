#!/bin/bash
# Docker环境检查脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo "=========================================="
echo "   Docker环境检查"
echo "=========================================="
echo ""

# 检查Docker是否安装
log_info "检查Docker..."
if command -v docker >/dev/null 2>&1; then
    version=$(docker --version)
    log_success "Docker已安装: $version"
else
    log_error "Docker未安装"
    exit 1
fi

# 检查Docker是否运行
log_info "检查Docker服务..."
if docker ps >/dev/null 2>&1; then
    log_success "Docker服务正在运行"
else
    log_error "Docker服务未运行"
    log_info "启动Docker: sudo systemctl start docker"
    exit 1
fi

# 检查Docker Compose
log_info "检查Docker Compose..."
if command -v docker-compose >/dev/null 2>&1; then
    version=$(docker-compose --version)
    log_success "Docker Compose已安装: $version"
elif docker compose version >/dev/null 2>&1; then
    version=$(docker compose version)
    log_success "Docker Compose已安装: $version"
else
    log_error "Docker Compose未安装"
    exit 1
fi

# 检查Docker权限
log_info "检查Docker权限..."
if docker ps >/dev/null 2>&1; then
    log_success "当前用户有Docker权限"
else
    log_error "当前用户没有Docker权限"
    log_info "添加权限: sudo usermod -aG docker $USER"
    log_info "然后重新登录或运行: newgrp docker"
    exit 1
fi

# 检查Docker磁盘空间
log_info "检查Docker磁盘空间..."
df_output=$(df -h /var/lib/docker 2>/dev/null || df -h /)
available=$(echo "$df_output" | awk 'NR==2 {print $4}')
log_success "可用磁盘空间: $available"

# 检查Docker镜像
log_info "检查Docker镜像..."
image_count=$(docker images -q | wc -l)
log_success "本地镜像数量: $image_count"

# 检查运行的容器
log_info "检查运行的容器..."
container_count=$(docker ps -q | wc -l)
log_success "运行中的容器: $container_count"

# 检查Docker网络
log_info "检查Docker网络..."
network_count=$(docker network ls | wc -l)
log_success "Docker网络数量: $((network_count - 1))"

echo ""
echo "=========================================="
echo "   环境检查完成 - 一切正常！"
echo "=========================================="

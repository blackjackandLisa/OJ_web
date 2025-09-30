#!/bin/bash
# 网络诊断脚本 - 诊断并修复常见网络问题

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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "   网络诊断和修复工具"
echo "=========================================="
echo ""

# 1. 检查基本网络连接
log_info "1. 检查基本网络连接..."
if ping -c 3 8.8.8.8 >/dev/null 2>&1; then
    log_success "基本网络连接正常"
else
    log_error "基本网络连接失败"
    log_info "尝试修复网络连接..."
    
    # 重启网络服务
    sudo systemctl restart networking 2>/dev/null || true
    sudo systemctl restart NetworkManager 2>/dev/null || true
    
    # 重新获取IP
    sudo dhclient -r 2>/dev/null || true
    sudo dhclient 2>/dev/null || true
    
    sleep 5
    
    if ping -c 3 8.8.8.8 >/dev/null 2>&1; then
        log_success "网络连接已修复"
    else
        log_error "无法修复网络连接，请检查网络配置"
        exit 1
    fi
fi

# 2. 检查DNS解析
log_info "2. 检查DNS解析..."
if nslookup google.com >/dev/null 2>&1; then
    log_success "DNS解析正常"
else
    log_warning "DNS解析失败，尝试修复..."
    
    # 配置DNS服务器
    sudo tee /etc/resolv.conf > /dev/null <<EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 114.114.114.114
nameserver 223.5.5.5
EOF
    
    if nslookup google.com >/dev/null 2>&1; then
        log_success "DNS解析已修复"
    else
        log_error "无法修复DNS解析"
    fi
fi

# 3. 检查Docker连接
log_info "3. 检查Docker连接..."
if ping -c 3 docker.io >/dev/null 2>&1; then
    log_success "Docker Hub连接正常"
else
    log_warning "Docker Hub连接失败"
fi

# 4. 检查防火墙
log_info "4. 检查防火墙状态..."
if command -v ufw >/dev/null 2>&1; then
    ufw_status=$(sudo ufw status | head -n 1)
    if [[ $ufw_status == *"active"* ]]; then
        log_warning "防火墙已启用: $ufw_status"
        log_info "如需关闭防火墙: sudo ufw disable"
    else
        log_success "防火墙未启用"
    fi
else
    log_info "未安装ufw防火墙"
fi

# 5. 检查Docker配置
log_info "5. 检查Docker配置..."
if [ -f "/etc/docker/daemon.json" ]; then
    log_info "Docker配置文件存在"
    cat /etc/docker/daemon.json
else
    log_warning "Docker配置文件不存在，创建默认配置..."
    
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"]
}
EOF
    
    # 重启Docker
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    
    log_success "Docker配置已创建并重启"
fi

# 6. 测试Docker镜像拉取
log_info "6. 测试Docker镜像拉取..."
if docker pull hello-world >/dev/null 2>&1; then
    log_success "Docker镜像拉取成功"
    docker rmi hello-world >/dev/null 2>&1
else
    log_error "Docker镜像拉取失败"
    log_info "建议使用本地镜像或离线部署"
fi

echo ""
echo "=========================================="
echo "   诊断完成"
echo "=========================================="

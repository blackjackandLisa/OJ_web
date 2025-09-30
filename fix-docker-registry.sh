#!/bin/bash
# Docker镜像源修复脚本 - 解决镜像拉取超时问题

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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "🔧 开始配置Docker镜像加速..."

# 创建Docker配置目录
sudo mkdir -p /etc/docker

# 备份原配置
if [ -f /etc/docker/daemon.json ]; then
    log_info "备份原配置文件..."
    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
fi

# 配置多个国内镜像源
log_info "配置国内镜像加速源..."
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.nastool.de",
    "https://docker.chenby.cn"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "max-concurrent-downloads": 10,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

log_success "镜像源配置完成！"

# 重启Docker服务
log_info "重启Docker服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

# 等待Docker启动
sleep 3

# 验证配置
log_info "验证Docker配置..."
if docker info | grep -i "registry mirrors" > /dev/null 2>&1; then
    log_success "✅ Docker镜像加速配置成功！"
    echo ""
    log_info "当前配置的镜像源："
    docker info | grep -A 5 "Registry Mirrors"
else
    log_warning "⚠️  无法验证镜像源配置，但已应用"
fi

echo ""
log_success "🎉 Docker镜像源修复完成！"
log_info "现在可以重新运行部署脚本了："
echo -e "${GREEN}./deploy-simple.sh${NC}"

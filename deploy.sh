#!/bin/bash
# Django OJ System - 统一部署脚本
# 支持自动检测环境并选择最佳部署方案

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Docker是否可用
check_docker() {
    if ! command_exists docker; then
        return 1
    fi
    
    if ! docker ps >/dev/null 2>&1; then
        return 1
    fi
    
    return 0
}

# 检查Docker Compose是否可用
check_docker_compose() {
    if command_exists docker-compose; then
        return 0
    elif docker compose version >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_success "网络连接正常"
        return 0
    else
        log_warning "网络连接失败"
        return 1
    fi
}

# 安装Docker
install_docker() {
    log_info "开始安装Docker..."
    
    # 更新包管理器
    sudo apt-get update
    
    # 安装依赖
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加Docker GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 添加当前用户到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "开始安装Docker Compose..."
    
    # 下载Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose安装完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f "docker.env" ]; then
        log_warning "docker.env不存在，创建默认配置..."
        
        cat > docker.env <<EOF
# Django Settings
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://oj_user:oj_password@db:5432/django_oj
POSTGRES_DB=django_oj
POSTGRES_USER=oj_user
POSTGRES_PASSWORD=$(openssl rand -base64 16)
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/1

# Security Settings
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Logging
LOG_LEVEL=INFO

# Judge Settings
JUDGE_ENGINE=docker
SANDBOX_ENABLED=True
EOF
        
        log_success "环境变量配置完成"
    else
        log_info "环境变量文件已存在"
    fi
}

# 构建Docker Judger镜像
build_judger() {
    log_info "构建Docker Judger镜像..."
    
    if [ -d "docker/judger" ]; then
        cd docker/judger
        docker build -t django-oj-judger:latest .
        cd ../..
        log_success "Docker Judger镜像构建完成"
    else
        log_warning "docker/judger目录不存在，跳过Judger构建"
    fi
}

# Docker部署
deploy_with_docker() {
    log_info "使用Docker部署..."
    
    # 停止旧容器
    log_info "停止旧容器..."
    docker-compose down 2>/dev/null || true
    
    # 构建并启动服务
    log_info "构建并启动服务..."
    docker-compose up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    log_info "检查服务状态..."
    docker-compose ps
    
    log_success "Docker部署完成！"
    log_info "访问地址: http://localhost"
}

# 本地部署（不使用Docker）
deploy_local() {
    log_info "使用本地环境部署..."
    
    # 检查Python
    if ! command_exists python3; then
        log_error "Python3未安装"
        exit 1
    fi
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r requirements.txt
    
    # 运行迁移
    log_info "运行数据库迁移..."
    python manage.py migrate
    
    # 创建默认模板
    log_info "创建默认模板..."
    python manage.py create_default_templates
    
    # 收集静态文件
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput
    
    # 启动服务
    log_info "启动Django开发服务器..."
    python manage.py runserver 0.0.0.0:8000
}

# 主函数
main() {
    echo "=========================================="
    echo "   Django OJ System - 部署脚本"
    echo "=========================================="
    echo ""
    
    # 检查操作系统
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warning "当前系统不是Linux，建议使用Linux系统部署"
    fi
    
    # 检查Docker
    if check_docker; then
        log_success "Docker已安装并运行"
        
        # 检查Docker Compose
        if check_docker_compose; then
            log_success "Docker Compose已安装"
        else
            log_warning "Docker Compose未安装"
            read -p "是否安装Docker Compose? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                install_docker_compose
            else
                log_error "需要Docker Compose才能继续"
                exit 1
            fi
        fi
        
        # 配置环境变量
        setup_environment
        
        # 构建Judger镜像
        build_judger
        
        # Docker部署
        deploy_with_docker
        
    else
        log_warning "Docker未安装或未运行"
        read -p "是否安装Docker? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_docker
            install_docker_compose
            
            log_warning "Docker安装完成，需要重新登录以应用用户组权限"
            log_info "请运行: newgrp docker"
            log_info "然后重新执行部署脚本"
            exit 0
        else
            log_info "使用本地环境部署..."
            deploy_local
        fi
    fi
}

# 运行主函数
main

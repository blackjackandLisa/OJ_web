#!/bin/bash
# 部署前完整检查脚本 - 检测所有潜在问题

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 统计变量
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

echo "=========================================="
echo "   Django OJ - 部署前完整检查"
echo "=========================================="
echo ""

# 检查函数
check() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    local test_name="$1"
    local test_command="$2"
    
    printf "%-50s" "$test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

warn() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
    local test_name="$1"
    printf "%-50s" "$test_name"
    echo -e "${YELLOW}[WARN]${NC}"
}

info() {
    local message="$1"
    echo -e "${BLUE}[INFO]${NC} $message"
}

# ==================== 系统环境检查 ====================
echo "🖥️  系统环境检查"
echo "----------------------------------------"

check "操作系统类型" "[ -f /etc/os-release ]"
if [ -f /etc/os-release ]; then
    OS_NAME=$(cat /etc/os-release | grep "^NAME=" | cut -d'"' -f2)
    OS_VERSION=$(cat /etc/os-release | grep "^VERSION=" | cut -d'"' -f2)
    info "操作系统: $OS_NAME $OS_VERSION"
fi

check "内存大小 (>= 2GB)" "[ $(free -m | awk '/^Mem:/{print $2}') -ge 2000 ]"
check "磁盘空间 (>= 10GB)" "[ $(df / | awk 'NR==2 {print int($4/1024/1024)}') -ge 10 ]"
check "CPU核心数 (>= 2)" "[ $(nproc) -ge 2 ]"

echo ""

# ==================== 必需软件检查 ====================
echo "📦 必需软件检查"
echo "----------------------------------------"

check "Docker已安装" "command -v docker"
check "Docker服务运行中" "docker ps"
check "Docker Compose已安装" "command -v docker-compose || docker compose version"
check "Git已安装" "command -v git"
check "curl已安装" "command -v curl"
check "Python3已安装" "command -v python3"

echo ""

# ==================== Docker环境检查 ====================
echo "🐳 Docker环境检查"
echo "----------------------------------------"

if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
    info "Docker版本: $DOCKER_VERSION"
    
    check "Docker可以运行容器" "docker run --rm hello-world"
    check "Docker磁盘空间充足" "[ $(docker system df -v 2>/dev/null | grep 'Local Volumes space usage' | awk '{print int($4)}' | sed 's/GB//' || echo '100') -lt 80 ]"
    
    # 检查Docker权限
    if docker ps >/dev/null 2>&1; then
        info "Docker权限: 当前用户有权限"
    else
        warn "Docker权限: 需要sudo或加入docker组"
        info "修复命令: sudo usermod -aG docker \$USER && newgrp docker"
    fi
fi

echo ""

# ==================== 网络连接检查 ====================
echo "🌐 网络连接检查"
echo "----------------------------------------"

check "基本网络连接 (8.8.8.8)" "ping -c 1 -W 2 8.8.8.8"
check "DNS解析正常" "nslookup google.com"
check "GitHub可访问" "curl -s --connect-timeout 5 https://github.com"
check "Docker Hub可访问" "curl -s --connect-timeout 5 https://hub.docker.com"

echo ""

# ==================== 项目文件检查 ====================
echo "📁 项目文件检查"
echo "----------------------------------------"

check "Dockerfile存在" "[ -f Dockerfile ]"
check "docker-compose.yml存在" "[ -f docker-compose.yml ]"
check "docker.env存在" "[ -f docker.env ]"
check "nginx.conf存在" "[ -f nginx.conf ]"
check "requirements-linux.txt存在" "[ -f requirements-linux.txt ]"
check "manage.py存在" "[ -f manage.py ]"
check "deploy.sh存在" "[ -f deploy.sh ]"

echo ""

# ==================== Docker配置文件检查 ====================
echo "🔧 配置文件检查"
echo "----------------------------------------"

# 检查Dockerfile
if [ -f Dockerfile ]; then
    check "Dockerfile包含pip安装修复" "grep -q 'EXTERNALLY-MANAGED' Dockerfile"
    check "Dockerfile包含break-system-packages" "grep -q 'break-system-packages' Dockerfile"
fi

# 检查docker-compose.yml
if [ -f docker-compose.yml ]; then
    check "docker-compose.yml包含web服务" "grep -q 'web:' docker-compose.yml"
    check "docker-compose.yml包含db服务" "grep -q 'db:' docker-compose.yml"
    check "docker-compose.yml包含redis服务" "grep -q 'redis:' docker-compose.yml"
    check "docker-compose.yml包含nginx服务" "grep -q 'nginx:' docker-compose.yml"
    check "docker-compose.yml包含健康检查" "grep -q 'healthcheck:' docker-compose.yml"
fi

# 检查docker.env
if [ -f docker.env ]; then
    check "docker.env包含SECRET_KEY" "grep -q 'SECRET_KEY' docker.env"
    check "docker.env包含DATABASE_URL" "grep -q 'DATABASE_URL' docker.env"
    check "docker.env包含JUDGE_ENGINE" "grep -q 'JUDGE_ENGINE' docker.env"
    
    # 安全检查
    if grep -q 'SECRET_KEY=your-secret-key-here' docker.env; then
        warn "SECRET_KEY使用默认值（生产环境需修改）"
        info "修复命令: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    fi
    
    if grep -q 'DEBUG=True' docker.env; then
        warn "DEBUG模式已启用（生产环境应关闭）"
        info "修复命令: 在docker.env中设置 DEBUG=False"
    fi
fi

echo ""

# ==================== Docker Judger检查 ====================
echo "⚖️  判题系统检查"
echo "----------------------------------------"

check "docker/judger目录存在" "[ -d docker/judger ]"
check "docker/judger/Dockerfile存在" "[ -f docker/judger/Dockerfile ]"
check "docker/judger/entrypoint.py存在" "[ -f docker/judger/entrypoint.py ]"
check "docker/judger/limits.conf存在" "[ -f docker/judger/limits.conf ]"

if [ -f docker/judger/Dockerfile ]; then
    check "Judger Dockerfile无UID冲突" "! grep -q 'useradd.*-u.*1000' docker/judger/Dockerfile"
fi

echo ""

# ==================== 端口检查 ====================
echo "🔌 端口占用检查"
echo "----------------------------------------"

check_port() {
    local port=$1
    local service=$2
    if ! netstat -tuln 2>/dev/null | grep -q ":$port " && ! ss -tuln 2>/dev/null | grep -q ":$port "; then
        check "$service端口 $port 可用" "true"
    else
        warn "$service端口 $port 已被占用"
        info "占用进程: $(lsof -i:$port 2>/dev/null | tail -1 || echo '未知')"
    fi
}

check_port 80 "HTTP"
check_port 443 "HTTPS"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"

echo ""

# ==================== 依赖包检查 ====================
echo "📚 Python依赖检查"
echo "----------------------------------------"

if [ -f requirements-linux.txt ]; then
    check "requirements包含Django" "grep -q '^Django==' requirements-linux.txt"
    check "requirements包含gunicorn" "grep -q '^gunicorn==' requirements-linux.txt"
    check "requirements包含psycopg2" "grep -q '^psycopg2' requirements-linux.txt"
    check "requirements包含docker" "grep -q '^docker==' requirements-linux.txt"
    check "requirements包含psutil" "grep -q '^psutil==' requirements-linux.txt"
fi

echo ""

# ==================== 安全检查 ====================
echo "🔒 安全配置检查"
echo "----------------------------------------"

if [ -f nginx.conf ]; then
    check "Nginx配置包含安全头" "grep -q 'X-Frame-Options' nginx.conf"
    check "Nginx配置包含CSP" "grep -q 'Content-Security-Policy' nginx.conf"
fi

if [ -f docker.env ]; then
    if grep -q 'ALLOWED_HOSTS=\*' docker.env; then
        warn "ALLOWED_HOSTS允许所有主机（不安全）"
    else
        check "ALLOWED_HOSTS已配置" "grep -q 'ALLOWED_HOSTS=' docker.env"
    fi
fi

echo ""

# ==================== 总结 ====================
echo "=========================================="
echo "   检查总结"
echo "=========================================="
echo -e "总检查项: $TOTAL_CHECKS"
echo -e "${GREEN}通过: $PASSED_CHECKS${NC}"
echo -e "${RED}失败: $FAILED_CHECKS${NC}"
echo -e "${YELLOW}警告: $WARNING_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过，可以开始部署！${NC}"
    echo ""
    echo "建议执行："
    echo "  ./deploy.sh"
    exit 0
elif [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  存在警告项，建议修复后再部署${NC}"
    echo ""
    echo "可以继续部署，但建议先处理警告项"
    exit 0
else
    echo -e "${RED}❌ 存在失败项，必须修复后才能部署${NC}"
    echo ""
    echo "请根据上述失败项进行修复"
    exit 1
fi

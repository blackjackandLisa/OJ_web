#!/bin/bash
# 构建Docker Judger镜像

set -e

echo "🐳 构建Docker Judger镜像..."

# 检查Docker是否可用
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 构建镜像
echo "📦 构建judger镜像..."
docker build -t django-oj-judger:latest ./docker/judger/

# 测试镜像
echo "🧪 测试judger镜像..."
docker run --rm django-oj-judger:latest python /app/entrypoint.py --help

echo "✅ Docker Judger镜像构建完成！"
echo ""
echo "📊 镜像信息："
docker images django-oj-judger:latest
echo ""
echo "🔧 使用方法："
echo "   - 在Django设置中设置 JUDGE_ENGINE=docker"
echo "   - 确保Docker服务正在运行"
echo "   - 判题将自动使用Docker容器执行"

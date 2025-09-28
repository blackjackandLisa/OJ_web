#!/bin/bash
# 生产环境部署脚本

set -e

echo "🚀 开始生产环境部署..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "docker.env" ]; then
    echo "❌ docker.env文件不存在，请先创建环境变量文件"
    exit 1
fi

# 生成新的SECRET_KEY（如果未设置）
if grep -q "your-secret-key-here-change-in-production" docker.env; then
    echo "⚠️  检测到默认SECRET_KEY，正在生成新的安全密钥..."
    NEW_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-secret-key-here-change-in-production/$NEW_SECRET_KEY/" docker.env
    echo "✅ 已生成新的SECRET_KEY"
fi

# 检查数据库密码
if grep -q "oj_password" docker.env; then
    echo "⚠️  检测到默认数据库密码，建议修改为强密码"
    echo "   请编辑docker.env文件中的POSTGRES_PASSWORD"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p media sandbox_tmp judge_temp logs

# 设置权限
echo "🔐 设置目录权限..."
chmod -R 755 media sandbox_tmp judge_temp logs

# 构建和启动服务
echo "🐳 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查服务健康状态..."
for i in {1..10}; do
    if curl -f http://localhost/health/ > /dev/null 2>&1; then
        echo "✅ 服务健康检查通过"
        break
    else
        echo "⏳ 等待服务就绪... ($i/10)"
        sleep 10
    fi
done

# 显示部署信息
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服务信息："
echo "   - Web应用: http://localhost"
echo "   - 管理界面: http://localhost/admin"
echo "   - 健康检查: http://localhost/health/"
echo ""
echo "🔧 管理命令："
echo "   - 查看日志: docker-compose logs -f"
echo "   - 重启服务: docker-compose restart"
echo "   - 停止服务: docker-compose down"
echo "   - 更新服务: docker-compose pull && docker-compose up -d"
echo ""
echo "⚠️  安全提醒："
echo "   1. 请修改docker.env中的数据库密码"
echo "   2. 配置域名和SSL证书"
echo "   3. 设置防火墙规则"
echo "   4. 配置定期备份"
echo ""
echo "📖 详细配置请参考: PRODUCTION_SECURITY.md"

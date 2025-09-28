#!/bin/bash
# 数据库初始化脚本

set -e

echo "🚀 开始数据库初始化..."

# 等待数据库启动
echo "⏳ 等待数据库启动..."
until python manage.py shell -c "from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
    echo "⏳ 数据库未就绪，等待5秒..."
    sleep 5
done

echo "✅ 数据库连接成功"

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
python manage.py migrate

# 创建超级用户
echo "👤 创建超级用户..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户创建成功 (用户名: admin, 密码: admin123)')
else:
    print('ℹ️  超级用户已存在')
EOF

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

echo "🎉 数据库初始化完成！"

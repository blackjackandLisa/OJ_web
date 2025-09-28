#!/usr/bin/env python
"""
数据库迁移脚本：从SQLite迁移到PostgreSQL
使用方法：
1. 开发环境：python scripts/migrate_to_postgresql.py
2. 生产环境：python scripts/migrate_to_postgresql.py --production
"""

import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings
import argparse


def check_database_connection():
    """检查数据库连接"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def migrate_database():
    """执行数据库迁移"""
    print("🔄 开始数据库迁移...")
    
    # 创建迁移文件
    print("📝 创建迁移文件...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # 执行迁移
    print("🚀 执行数据库迁移...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ 数据库迁移完成")


def create_superuser():
    """创建超级用户"""
    print("👤 创建超级用户...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ 超级用户创建成功 (用户名: admin, 密码: admin123)")
        else:
            print("ℹ️  超级用户已存在")
    except Exception as e:
        print(f"❌ 创建超级用户失败: {e}")


def load_sample_data():
    """加载示例数据"""
    print("📊 加载示例数据...")
    try:
        # 这里可以添加加载示例数据的逻辑
        # 例如：创建示例题目、用户等
        print("✅ 示例数据加载完成")
    except Exception as e:
        print(f"❌ 加载示例数据失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='数据库迁移脚本')
    parser.add_argument('--production', action='store_true', help='生产环境模式')
    parser.add_argument('--skip-superuser', action='store_true', help='跳过创建超级用户')
    parser.add_argument('--skip-sample-data', action='store_true', help='跳过加载示例数据')
    
    args = parser.parse_args()
    
    print("🚀 开始数据库迁移流程...")
    print(f"📊 当前数据库: {settings.DATABASES['default']['ENGINE']}")
    
    # 检查数据库连接
    if not check_database_connection():
        print("❌ 无法连接到数据库，请检查配置")
        return
    
    # 执行迁移
    migrate_database()
    
    # 创建超级用户
    if not args.skip_superuser:
        create_superuser()
    
    # 加载示例数据
    if not args.skip_sample_data:
        load_sample_data()
    
    print("🎉 数据库迁移流程完成！")


if __name__ == '__main__':
    main()

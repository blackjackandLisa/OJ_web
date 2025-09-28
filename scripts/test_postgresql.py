#!/usr/bin/env python
"""
测试PostgreSQL连接脚本
使用方法：
1. 开发环境：python scripts/test_postgresql.py
2. 生产环境：python scripts/test_postgresql.py --production
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

from django.db import connection
from django.conf import settings
import argparse


def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    print(f"📊 数据库引擎: {settings.DATABASES['default']['ENGINE']}")
    print(f"📊 数据库名称: {settings.DATABASES['default']['NAME']}")
    print(f"📊 数据库主机: {settings.DATABASES['default']['HOST']}")
    print(f"📊 数据库端口: {settings.DATABASES['default']['PORT']}")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL版本: {version}")
            
            # 测试基本查询
            cursor.execute("SELECT 1 as test;")
            result = cursor.fetchone()
            print(f"✅ 基本查询测试成功: {result}")
            
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_django_models():
    """测试Django模型"""
    print("🔍 测试Django模型...")
    try:
        from django.contrib.auth import get_user_model
        from problems.models import Problem
        from submissions.models import Submission
        
        User = get_user_model()
        
        # 测试用户模型
        user_count = User.objects.count()
        print(f"✅ 用户模型测试成功，用户数量: {user_count}")
        
        # 测试题目模型
        problem_count = Problem.objects.count()
        print(f"✅ 题目模型测试成功，题目数量: {problem_count}")
        
        # 测试提交模型
        submission_count = Submission.objects.count()
        print(f"✅ 提交模型测试成功，提交数量: {submission_count}")
        
        return True
    except Exception as e:
        print(f"❌ Django模型测试失败: {e}")
        return False


def test_redis_connection():
    """测试Redis连接"""
    print("🔍 测试Redis连接...")
    try:
        from django.core.cache import cache
        
        # 测试缓存写入
        cache.set('test_key', 'test_value', 30)
        result = cache.get('test_key')
        
        if result == 'test_value':
            print("✅ Redis连接测试成功")
            return True
        else:
            print("❌ Redis缓存测试失败")
            return False
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='测试PostgreSQL连接')
    parser.add_argument('--production', action='store_true', help='生产环境模式')
    
    args = parser.parse_args()
    
    print("🚀 开始数据库连接测试...")
    
    # 测试数据库连接
    if not test_database_connection():
        print("❌ 数据库连接测试失败")
        return
    
    # 测试Django模型
    if not test_django_models():
        print("❌ Django模型测试失败")
        return
    
    # 测试Redis连接
    if not test_redis_connection():
        print("❌ Redis连接测试失败")
        return
    
    print("🎉 所有测试通过！数据库配置正确！")


if __name__ == '__main__':
    main()

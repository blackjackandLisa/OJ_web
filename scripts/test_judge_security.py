#!/usr/bin/env python
"""
判题系统安全测试脚本
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

from judge.engine_factory import JudgeEngineFactory
from judge.models import JudgeConfig, Problem, TestCase
from accounts.models import User
from submissions.models import Submission


def test_judge_engines():
    """测试所有可用的判题引擎"""
    print("🔍 测试判题引擎...")
    
    # 获取可用引擎
    available_engines = JudgeEngineFactory.get_available_engines()
    print(f"📊 可用引擎: {available_engines}")
    
    # 测试每个引擎
    for engine_type in available_engines:
        print(f"\n🧪 测试 {engine_type} 引擎...")
        
        try:
            if JudgeEngineFactory.test_engine(engine_type):
                print(f"✅ {engine_type} 引擎可用")
            else:
                print(f"❌ {engine_type} 引擎不可用")
        except Exception as e:
            print(f"❌ {engine_type} 引擎测试失败: {e}")


def test_malicious_code():
    """测试恶意代码防护"""
    print("\n🛡️ 测试恶意代码防护...")
    
    # 恶意代码示例
    malicious_codes = [
        {
            'name': '文件系统访问',
            'code': '''
import os
with open("/etc/passwd", "r") as f:
    print(f.read())
''',
            'language': 'python'
        },
        {
            'name': '网络访问',
            'code': '''
import urllib.request
response = urllib.request.urlopen("http://example.com")
print(response.read().decode())
''',
            'language': 'python'
        },
        {
            'name': '系统命令执行',
            'code': '''
import subprocess
result = subprocess.run(["ls", "/"], capture_output=True, text=True)
print(result.stdout)
''',
            'language': 'python'
        },
        {
            'name': '无限循环',
            'code': '''
while True:
    pass
''',
            'language': 'python'
        }
    ]
    
    # 创建测试引擎
    engine = JudgeEngineFactory.create_engine()
    print(f"📊 使用引擎: {type(engine).__name__}")
    
    for test_case in malicious_codes:
        print(f"\n🔍 测试: {test_case['name']}")
        
        try:
            # 创建临时提交
            user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            problem, _ = Problem.objects.get_or_create(
                title='安全测试题目',
                defaults={
                    'description': '测试题目',
                    'time_limit': 1000,
                    'memory_limit': 128
                }
            )
            
            test_case_obj, _ = TestCase.objects.get_or_create(
                problem=problem,
                input_data='test input',
                expected_output='test output',
                is_sample=False
            )
            
            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=test_case['code'],
                language=test_case['language']
            )
            
            # 执行判题
            result = engine.judge_submission(submission)
            
            print(f"   状态: {result['status']}")
            print(f"   得分: {result['score']}")
            if result.get('error_message'):
                print(f"   错误: {result['error_message']}")
            
            # 清理
            submission.delete()
            test_case_obj.delete()
            problem.delete()
            user.delete()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")


def test_resource_limits():
    """测试资源限制"""
    print("\n⚡ 测试资源限制...")
    
    # 资源消耗代码
    resource_tests = [
        {
            'name': '内存消耗',
            'code': '''
data = []
for i in range(1000000):
    data.append("x" * 1000)
print("内存测试完成")
''',
            'language': 'python'
        },
        {
            'name': 'CPU消耗',
            'code': '''
import time
start = time.time()
while time.time() - start < 10:
    pass
print("CPU测试完成")
''',
            'language': 'python'
        }
    ]
    
    engine = JudgeEngineFactory.create_engine()
    
    for test_case in resource_tests:
        print(f"\n🔍 测试: {test_case['name']}")
        
        try:
            # 创建测试提交
            user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            problem, _ = Problem.objects.get_or_create(
                title='资源测试题目',
                defaults={
                    'description': '测试题目',
                    'time_limit': 2000,  # 2秒
                    'memory_limit': 64   # 64MB
                }
            )
            
            test_case_obj, _ = TestCase.objects.get_or_create(
                problem=problem,
                input_data='',
                expected_output='',
                is_sample=False
            )
            
            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=test_case['code'],
                language=test_case['language']
            )
            
            # 执行判题
            result = engine.judge_submission(submission)
            
            print(f"   状态: {result['status']}")
            print(f"   时间: {result.get('time_used', 0)}ms")
            print(f"   内存: {result.get('memory_used', 0)}KB")
            
            # 清理
            submission.delete()
            test_case_obj.delete()
            problem.delete()
            user.delete()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")


def main():
    """主函数"""
    print("🚀 判题系统安全测试")
    print("=" * 50)
    
    # 测试引擎可用性
    test_judge_engines()
    
    # 测试恶意代码防护
    test_malicious_code()
    
    # 测试资源限制
    test_resource_limits()
    
    print("\n🎉 安全测试完成！")
    print("\n📊 测试总结：")
    print("   - 检查了所有可用判题引擎")
    print("   - 测试了恶意代码防护能力")
    print("   - 验证了资源限制功能")
    print("\n⚠️  建议：")
    print("   - 生产环境使用Docker引擎")
    print("   - 定期更新安全配置")
    print("   - 监控判题系统日志")


if __name__ == '__main__':
    main()

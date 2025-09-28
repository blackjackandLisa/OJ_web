"""
Django管理命令：构建Docker Judger镜像
"""
import os
import subprocess
import sys
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = '构建Docker Judger镜像'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-windows-check',
            action='store_true',
            help='跳过Windows环境检查'
        )

    def handle(self, *args, **options):
        # 检查平台
        if sys.platform == 'win32' and not options['skip_windows_check']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  检测到Windows环境，Docker Judger主要用于Linux生产环境\n'
                    '如需在Windows上测试，请使用 --skip-windows-check 参数'
                )
            )
            return

        # 检查Docker是否可用
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.stdout.write(f"✅ Docker版本: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.stdout.write(
                self.style.ERROR('❌ Docker未安装或不可用，请先安装Docker')
            )
            return

        # 构建镜像
        self.stdout.write('🐳 开始构建Docker Judger镜像...')
        
        try:
            # 构建命令
            build_cmd = [
                'docker', 'build',
                '-t', 'django-oj-judger:latest',
                './docker/judger/'
            ]
            
            # 执行构建
            result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Docker Judger镜像构建成功！')
            )
            
            # 测试镜像
            self.stdout.write('🧪 测试镜像...')
            test_cmd = [
                'docker', 'run', '--rm',
                'django-oj-judger:latest',
                'python', '/app/entrypoint.py', '--help'
            ]
            
            subprocess.run(test_cmd, check=True, capture_output=True)
            self.stdout.write(self.style.SUCCESS('✅ 镜像测试通过！'))
            
            # 显示使用说明
            self.stdout.write('')
            self.stdout.write('📊 使用说明：')
            self.stdout.write('   1. 在docker.env中设置: JUDGE_ENGINE=docker')
            self.stdout.write('   2. 重启Django服务')
            self.stdout.write('   3. 判题将自动使用Docker容器执行')
            self.stdout.write('')
            self.stdout.write('🔧 查看镜像: docker images django-oj-judger:latest')
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 构建失败: {e.stderr}')
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 构建错误: {str(e)}')
            )
            return

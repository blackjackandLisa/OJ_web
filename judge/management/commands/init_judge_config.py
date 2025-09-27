from django.core.management.base import BaseCommand
from judge.models import JudgeConfig


class Command(BaseCommand):
    help = '初始化判题配置'

    def handle(self, *args, **options):
        configs = [
            {
                'language': 'python',
                'compile_command': '',  # Python不需要编译
                'run_command': 'python {file_path}',
                'file_extension': '.py',
                'time_limit_multiplier': 1.0,
                'memory_limit_multiplier': 1.0,
            },
            {
                'language': 'cpp',
                'compile_command': 'g++ -o {file_path}.exe {file_path} -std=c++17 -O2',
                'run_command': '{file_path}.exe',
                'file_extension': '.cpp',
                'time_limit_multiplier': 1.0,
                'memory_limit_multiplier': 1.0,
            },
            {
                'language': 'java',
                'compile_command': 'javac {file_path}',
                'run_command': 'java -cp {dir} {class_name}',
                'file_extension': '.java',
                'time_limit_multiplier': 2.0,  # Java启动较慢
                'memory_limit_multiplier': 1.5,  # Java内存开销较大
            },
            {
                'language': 'javascript',
                'compile_command': '',  # JavaScript不需要编译
                'run_command': 'node {file_path}',
                'file_extension': '.js',
                'time_limit_multiplier': 1.0,
                'memory_limit_multiplier': 1.0,
            },
        ]

        created_count = 0
        updated_count = 0

        for config_data in configs:
            config, created = JudgeConfig.objects.get_or_create(
                language=config_data['language'],
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建 {config_data["language"]} 配置')
                )
            else:
                # 更新现有配置
                for key, value in config_data.items():
                    if key != 'language':
                        setattr(config, key, value)
                config.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新 {config_data["language"]} 配置')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'判题配置初始化完成: 创建 {created_count} 个，更新 {updated_count} 个'
            )
        )

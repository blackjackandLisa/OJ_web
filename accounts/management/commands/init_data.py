from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from problems.models import Category, Tag, Problem
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = '初始化OJ系统的基础数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化基础数据...')
        
        # 创建分类
        self.create_categories()
        
        # 创建标签
        self.create_tags()
        
        # 创建示例题目
        self.create_sample_problems()
        
        self.stdout.write(
            self.style.SUCCESS('基础数据初始化完成！')
        )

    def create_categories(self):
        """创建题目分类"""
        categories = [
            {'name': '基础算法', 'description': '基础算法题目', 'color': '#28a745'},
            {'name': '数据结构', 'description': '数据结构相关题目', 'color': '#007bff'},
            {'name': '动态规划', 'description': '动态规划题目', 'color': '#ffc107'},
            {'name': '图论', 'description': '图论算法题目', 'color': '#dc3545'},
            {'name': '数学', 'description': '数学相关题目', 'color': '#6f42c1'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'创建分类: {category.name}')
            else:
                self.stdout.write(f'分类已存在: {category.name}')

    def create_tags(self):
        """创建题目标签"""
        tags = [
            '排序', '搜索', '贪心', '递归', '分治', '回溯',
            '数组', '链表', '栈', '队列', '树', '图',
            '字符串', '数学', '几何', '模拟', '枚举'
        ]
        
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f'创建标签: {tag.name}')
            else:
                self.stdout.write(f'标签已存在: {tag.name}')

    def create_sample_problems(self):
        """创建示例题目"""
        # 获取管理员用户
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('未找到管理员用户，跳过创建示例题目')
            )
            return
        
        # 获取分类和标签
        basic_category = Category.objects.filter(name='基础算法').first()
        array_tag = Tag.objects.filter(name='数组').first()
        math_tag = Tag.objects.filter(name='数学').first()
        
        problems = [
            {
                'title': 'A + B Problem',
                'description': '计算两个整数的和。\n\n给定两个整数 a 和 b，计算 a + b 的值。',
                'input_format': '输入包含两个整数 a 和 b，用空格分隔。',
                'output_format': '输出 a + b 的值。',
                'sample_input': '1 2',
                'sample_output': '3',
                'hint': '这是一个最基础的题目，注意输入输出格式。',
                'time_limit': 1000,
                'memory_limit': 256,
                'difficulty': 'easy',
                'category': basic_category,
                'tags': [array_tag, math_tag] if array_tag and math_tag else [],
            },
            {
                'title': '最大子数组和',
                'description': '给定一个整数数组，找到一个具有最大和的连续子数组（至少包含一个元素），返回其最大和。\n\n示例：\n输入: [-2,1,-3,4,-1,2,1,-5,4]\n输出: 6\n解释: 连续子数组 [4,-1,2,1] 的和最大，为 6。',
                'input_format': '第一行包含一个整数 n，表示数组长度。\n第二行包含 n 个整数，表示数组元素。',
                'output_format': '输出最大子数组和。',
                'sample_input': '9\n-2 1 -3 4 -1 2 1 -5 4',
                'sample_output': '6',
                'hint': '可以使用动态规划或贪心算法解决。',
                'time_limit': 2000,
                'memory_limit': 512,
                'difficulty': 'medium',
                'category': basic_category,
                'tags': [array_tag] if array_tag else [],
            }
        ]
        
        for prob_data in problems:
            # 提取标签数据
            tags = prob_data.pop('tags', [])
            
            problem, created = Problem.objects.get_or_create(
                title=prob_data['title'],
                defaults={
                    **prob_data,
                    'author': admin_user,
                    'is_public': True,
                }
            )
            
            if created:
                # 添加标签
                if tags:
                    problem.tags.set(tags)
                
                self.stdout.write(f'创建题目: {problem.title}')
            else:
                self.stdout.write(f'题目已存在: {problem.title}')

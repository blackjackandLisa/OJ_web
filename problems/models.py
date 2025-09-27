from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """题目分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '题目分类'
        verbose_name_plural = '题目分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """题目标签"""
    name = models.CharField(max_length=30, unique=True, verbose_name='标签名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '题目标签'
        verbose_name_plural = '题目标签'
        ordering = ['name']

    def __str__(self):
        return self.name


class Problem(models.Model):
    """题目模型"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]

    title = models.CharField(max_length=200, verbose_name='题目标题')
    description = models.TextField(verbose_name='题目描述')
    input_format = models.TextField(verbose_name='输入格式')
    output_format = models.TextField(verbose_name='输出格式')
    sample_input = models.TextField(verbose_name='样例输入')
    sample_output = models.TextField(verbose_name='样例输出')
    hint = models.TextField(blank=True, verbose_name='提示')
    time_limit = models.PositiveIntegerField(default=1000, verbose_name='时间限制(ms)')
    memory_limit = models.PositiveIntegerField(default=256, verbose_name='内存限制(MB)')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy', verbose_name='难度')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者', null=True, blank=True)
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    total_submissions = models.PositiveIntegerField(default=0, verbose_name='总提交数')
    accepted_submissions = models.PositiveIntegerField(default=0, verbose_name='通过提交数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def acceptance_rate(self):
        """通过率"""
        if self.total_submissions == 0:
            return 0
        return round(self.accepted_submissions / self.total_submissions * 100, 2)


class TestCase(models.Model):
    """测试用例"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases', verbose_name='题目')
    input_data = models.TextField(verbose_name='输入数据')
    expected_output = models.TextField(verbose_name='期望输出')
    is_sample = models.BooleanField(default=False, verbose_name='是否为样例')
    order = models.PositiveIntegerField(default=0, verbose_name='顺序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['order']

    def __str__(self):
        return f"{self.problem.title} - 测试用例 {self.order}"


class GlobalTemplate(models.Model):
    """全局代码模板"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('go', 'Go'),
        ('rust', 'Rust'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='模板名称')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name='编程语言')
    template_code = models.TextField(verbose_name='模板代码')
    description = models.TextField(blank=True, verbose_name='模板描述')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '全局模板'
        verbose_name_plural = '全局模板'
        unique_together = ['name', 'language']
        ordering = ['language', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"


class ProblemTemplate(models.Model):
    """题目特定代码模板"""
    LANGUAGE_CHOICES = GlobalTemplate.LANGUAGE_CHOICES
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='templates', verbose_name='题目')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name='编程语言')
    template_code = models.TextField(verbose_name='模板代码')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认模板')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '题目模板'
        verbose_name_plural = '题目模板'
        unique_together = ['problem', 'language']
        ordering = ['problem', 'language']
    
    def __str__(self):
        return f"{self.problem.title} - {self.get_language_display()}模板"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class JudgeConfig(models.Model):
    """判题配置"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
    ]

    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, unique=True, verbose_name='编程语言')
    compile_command = models.CharField(max_length=200, verbose_name='编译命令')
    run_command = models.CharField(max_length=200, verbose_name='运行命令')
    file_extension = models.CharField(max_length=10, verbose_name='文件扩展名')
    time_limit_multiplier = models.FloatField(default=1.0, verbose_name='时间限制倍数')
    memory_limit_multiplier = models.FloatField(default=1.0, verbose_name='内存限制倍数')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '评测配置'
        verbose_name_plural = '评测配置'
        ordering = ['language']

    def __str__(self):
        return f"{self.get_language_display()} 配置"


class JudgeQueue(models.Model):
    """判题队列"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    submission = models.OneToOneField('submissions.Submission', on_delete=models.CASCADE, verbose_name='提交记录')
    priority = models.PositiveIntegerField(default=0, verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='队列状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='入队时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')

    class Meta:
        verbose_name = '评测队列'
        verbose_name_plural = '评测队列'
        ordering = ['-priority', 'created_at']

    def __str__(self):
        return f"队列 #{self.id} - {self.submission.user.username} - {self.status}"


class JudgeResult(models.Model):
    """判题结果"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('judging', '评测中'),
        ('accepted', '通过'),
        ('wrong_answer', '答案错误'),
        ('time_limit_exceeded', '超时'),
        ('memory_limit_exceeded', '内存超限'),
        ('runtime_error', '运行时错误'),
        ('compile_error', '编译错误'),
        ('system_error', '系统错误'),
    ]

    submission = models.OneToOneField('submissions.Submission', on_delete=models.CASCADE, verbose_name='提交记录')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending', verbose_name='评测状态')
    score = models.PositiveIntegerField(default=0, verbose_name='得分')
    time_used = models.PositiveIntegerField(null=True, blank=True, verbose_name='运行时间(ms)')
    memory_used = models.PositiveIntegerField(null=True, blank=True, verbose_name='内存使用(KB)')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    test_results = models.JSONField(default=list, blank=True, verbose_name='测试结果详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '评测结果'
        verbose_name_plural = '评测结果'
        ordering = ['-created_at']

    def __str__(self):
        return f"结果 #{self.id} - {self.submission.user.username} - {self.status}"

    @property
    def is_accepted(self):
        return self.status == 'accepted'

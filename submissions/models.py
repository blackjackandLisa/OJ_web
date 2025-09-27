from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Submission(models.Model):
    """代码提交记录"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
    ]

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    problem = models.ForeignKey('problems.Problem', on_delete=models.CASCADE, verbose_name='题目')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name='编程语言')
    code = models.TextField(verbose_name='代码')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    time_used = models.PositiveIntegerField(null=True, blank=True, verbose_name='运行时间(ms)')
    memory_used = models.PositiveIntegerField(null=True, blank=True, verbose_name='内存使用(KB)')
    score = models.PositiveIntegerField(default=0, verbose_name='得分')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    test_results = models.JSONField(default=list, blank=True, verbose_name='测试结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    class Meta:
        verbose_name = '提交记录'
        verbose_name_plural = '提交记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"

    @property
    def is_accepted(self):
        return self.status == 'accepted'

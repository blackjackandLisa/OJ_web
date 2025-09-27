from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    school = models.CharField(max_length=100, blank=True, verbose_name='学校')
    student_id = models.CharField(max_length=20, blank=True, verbose_name='学号')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    solved_problems = models.ManyToManyField('problems.Problem', blank=True, related_name='solvers', verbose_name='已解决题目')
    total_submissions = models.PositiveIntegerField(default=0, verbose_name='总提交数')
    accepted_submissions = models.PositiveIntegerField(default=0, verbose_name='通过提交数')
    rating = models.IntegerField(default=1200, verbose_name='积分')
    is_verified = models.BooleanField(default=False, verbose_name='是否验证')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-rating', 'username']

    def __str__(self):
        return self.username

    @property
    def acceptance_rate(self):
        """通过率"""
        if self.total_submissions == 0:
            return 0
        return round(self.accepted_submissions / self.total_submissions * 100, 2)
    
    def update_submission_stats(self):
        """更新提交统计"""
        from submissions.models import Submission
        self.total_submissions = Submission.objects.filter(user=self).count()
        self.accepted_submissions = Submission.objects.filter(user=self, status='accepted').count()
        self.save(update_fields=['total_submissions', 'accepted_submissions'])
    
    def get_rank(self):
        """获取用户排名"""
        return User.objects.filter(rating__gt=self.rating).count() + 1


class UserActivityLog(models.Model):
    """用户活动日志"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('register', '注册'),
        ('profile_update', '更新资料'),
        ('password_change', '修改密码'),
        ('submission', '提交代码'),
        ('problem_solve', '解决题目'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    description = models.CharField(max_length=200, verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '用户活动日志'
        verbose_name_plural = '用户活动日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class UserRanking(models.Model):
    """用户排行榜缓存"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    rank = models.PositiveIntegerField(verbose_name='排名')
    rating = models.IntegerField(verbose_name='积分')
    solved_count = models.PositiveIntegerField(verbose_name='解决题目数')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户排行榜'
        verbose_name_plural = '用户排行榜'
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.user.username} - 第{self.rank}名"

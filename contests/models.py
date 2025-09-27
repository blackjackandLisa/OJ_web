from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Contest(models.Model):
    """竞赛模型"""
    STATUS_CHOICES = [
        ('upcoming', '即将开始'),
        ('running', '进行中'),
        ('finished', '已结束'),
    ]

    title = models.CharField(max_length=200, verbose_name='竞赛标题')
    description = models.TextField(verbose_name='竞赛描述')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    duration = models.PositiveIntegerField(verbose_name='持续时间(分钟)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='状态')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    password = models.CharField(max_length=50, blank=True, verbose_name='密码')
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name='最大参与人数')
    problems = models.ManyToManyField('problems.Problem', through='ContestProblem', verbose_name='题目')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '竞赛'
        verbose_name_plural = '竞赛'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def participant_count(self):
        return self.participants.count()


class ContestProblem(models.Model):
    """竞赛题目关联"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name='竞赛')
    problem = models.ForeignKey('problems.Problem', on_delete=models.CASCADE, verbose_name='题目')
    order = models.PositiveIntegerField(verbose_name='题目顺序')
    points = models.PositiveIntegerField(default=100, verbose_name='分值')

    class Meta:
        verbose_name = '竞赛题目'
        verbose_name_plural = '竞赛题目'
        unique_together = ['contest', 'problem']
        ordering = ['order']

    def __str__(self):
        return f"{self.contest.title} - {self.problem.title}"


class ContestParticipation(models.Model):
    """竞赛参与记录"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='participants', verbose_name='竞赛')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='参与时间')
    score = models.PositiveIntegerField(default=0, verbose_name='总得分')
    solved_count = models.PositiveIntegerField(default=0, verbose_name='解决题目数')
    penalty = models.PositiveIntegerField(default=0, verbose_name='罚时(分钟)')

    class Meta:
        verbose_name = '竞赛参与'
        verbose_name_plural = '竞赛参与'
        unique_together = ['contest', 'user']
        ordering = ['-score', 'penalty']

    def __str__(self):
        return f"{self.user.username} - {self.contest.title}"


class ContestSubmission(models.Model):
    """竞赛提交记录"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name='竞赛')
    submission = models.OneToOneField('submissions.Submission', on_delete=models.CASCADE, verbose_name='提交记录')
    problem = models.ForeignKey(ContestProblem, on_delete=models.CASCADE, verbose_name='竞赛题目')
    is_first_ac = models.BooleanField(default=False, verbose_name='是否首次通过')
    penalty_time = models.PositiveIntegerField(default=0, verbose_name='罚时')

    class Meta:
        verbose_name = '竞赛提交'
        verbose_name_plural = '竞赛提交'

    def __str__(self):
        return f"{self.submission.user.username} - {self.contest.title} - {self.problem.problem.title}"

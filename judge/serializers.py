from rest_framework import serializers
from .models import JudgeConfig, JudgeQueue, JudgeResult


class JudgeConfigSerializer(serializers.ModelSerializer):
    """判题配置序列化器"""
    class Meta:
        model = JudgeConfig
        fields = '__all__'


class JudgeQueueSerializer(serializers.ModelSerializer):
    """判题队列序列化器"""
    submission_info = serializers.SerializerMethodField()
    
    class Meta:
        model = JudgeQueue
        fields = '__all__'
    
    def get_submission_info(self, obj):
        return {
            'id': obj.submission.id,
            'user': obj.submission.user.username,
            'problem': obj.submission.problem.title,
            'language': obj.submission.get_language_display(),
            'status': obj.submission.get_status_display(),
        }


class JudgeResultSerializer(serializers.ModelSerializer):
    """判题结果序列化器"""
    submission_info = serializers.SerializerMethodField()
    
    class Meta:
        model = JudgeResult
        fields = '__all__'
    
    def get_submission_info(self, obj):
        return {
            'id': obj.submission.id,
            'user': obj.submission.user.username,
            'problem': obj.submission.problem.title,
            'language': obj.submission.get_language_display(),
            'code': obj.submission.code,
        }

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import JudgeConfig, JudgeQueue, JudgeResult
from .serializers import JudgeConfigSerializer, JudgeQueueSerializer, JudgeResultSerializer
from .tasks import rejudge_submission


class JudgeConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """判题配置API视图集"""
    queryset = JudgeConfig.objects.filter(is_enabled=True)
    serializer_class = JudgeConfigSerializer
    permission_classes = [IsAuthenticated]


class JudgeQueueViewSet(viewsets.ReadOnlyModelViewSet):
    """判题队列API视图集"""
    queryset = JudgeQueue.objects.all()
    serializer_class = JudgeQueueSerializer
    permission_classes = [IsAdminUser]


class JudgeResultViewSet(viewsets.ReadOnlyModelViewSet):
    """判题结果API视图集"""
    queryset = JudgeResult.objects.all()
    serializer_class = JudgeResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """普通用户只能查看自己的判题结果"""
        if self.request.user.is_staff:
            return JudgeResult.objects.all()
        return JudgeResult.objects.filter(submission__user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rejudge(self, request, pk=None):
        """重新判题"""
        judge_result = self.get_object()
        submission = judge_result.submission
        
        # 检查权限：只有提交者或管理员可以重新判题
        if not (request.user == submission.user or request.user.is_staff):
            return Response(
                {'error': '没有权限重新判题'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rejudge_submission(submission)
            return Response({'message': '重新判题已开始'})
        except Exception as e:
            return Response(
                {'error': f'重新判题失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@login_required
def judge_status_view(request):
    """判题状态页面"""
    # 获取用户的提交记录
    user_submissions = request.user.submission_set.all().order_by('-created_at')[:20]
    
    # 获取队列状态（仅管理员）
    queue_status = None
    if request.user.is_staff:
        queue_status = {
            'pending': JudgeQueue.objects.filter(status='pending').count(),
            'processing': JudgeQueue.objects.filter(status='processing').count(),
            'completed': JudgeQueue.objects.filter(status='completed').count(),
            'failed': JudgeQueue.objects.filter(status='failed').count(),
        }
    
    context = {
        'user_submissions': user_submissions,
        'queue_status': queue_status,
    }
    return render(request, 'judge/status.html', context)

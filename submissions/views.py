from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionCreateSerializer


def submission_list(request):
    """提交记录列表页面"""
    submissions = Submission.objects.all().order_by('-created_at')
    
    # 筛选逻辑
    user_id = request.GET.get('user')
    problem_id = request.GET.get('problem')
    status = request.GET.get('status')
    language = request.GET.get('language')
    
    if user_id:
        submissions = submissions.filter(user_id=user_id)
    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)
    if status:
        submissions = submissions.filter(status=status)
    if language:
        submissions = submissions.filter(language=language)
    
    context = {
        'submissions': submissions,
        'current_user': user_id,
        'current_problem': problem_id,
        'current_status': status,
        'current_language': language,
    }
    return render(request, 'submissions/list.html', context)


def submission_detail(request, submission_id):
    """提交记录详情页面"""
    submission = get_object_or_404(Submission, id=submission_id)
    context = {'submission': submission}
    return render(request, 'submissions/detail.html', context)


@login_required
def submission_status_api(request, submission_id):
    """提交状态轮询接口"""
    submission = get_object_or_404(Submission, id=submission_id)

    # 权限校验：仅提交者或管理员可查看
    if not (request.user == submission.user or request.user.is_staff):
        return JsonResponse({'error': '没有权限查看该提交'}, status=403)

    status_badge_class = {
        'accepted': 'bg-success',
        'wrong_answer': 'bg-danger',
        'time_limit_exceeded': 'bg-warning',
        'memory_limit_exceeded': 'bg-info',
        'runtime_error': 'bg-danger',
        'compile_error': 'bg-secondary',
        'system_error': 'bg-dark',
    }.get(submission.status, 'bg-primary')

    data = {
        'id': submission.id,
        'status': submission.status,
        'status_display': submission.get_status_display(),
        'is_finished': submission.status not in ['pending', 'judging'],
        'badge_class': status_badge_class,
        'time_used': submission.time_used,
        'memory_used': submission.memory_used,
        'score': submission.score,
        'error_message': submission.error_message or '',
        'test_results': submission.test_results or [],
    }

    return JsonResponse(data)


class SubmissionViewSet(viewsets.ModelViewSet):
    """提交记录API视图集"""
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Submission.objects.all()
        return Submission.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SubmissionCreateSerializer
        return SubmissionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Contest, ContestParticipation
from .serializers import (
    ContestListSerializer, ContestDetailSerializer, 
    ContestCreateSerializer, ContestParticipationSerializer
)


def contest_list(request):
    """竞赛列表页面"""
    contests = Contest.objects.filter(is_public=True).order_by('-created_at')
    context = {'contests': contests}
    return render(request, 'contests/list.html', context)


def contest_detail(request, contest_id):
    """竞赛详情页面"""
    contest = get_object_or_404(Contest, id=contest_id, is_public=True)
    context = {'contest': contest}
    return render(request, 'contests/detail.html', context)


@login_required
def join_contest(request, contest_id):
    """参加竞赛"""
    contest = get_object_or_404(Contest, id=contest_id, is_public=True)
    # 处理参加竞赛逻辑
    return render(request, 'contests/join.html', {'contest': contest})


def leaderboard(request, contest_id):
    """竞赛排行榜"""
    contest = get_object_or_404(Contest, id=contest_id, is_public=True)
    participations = ContestParticipation.objects.filter(contest=contest).order_by('-score', 'penalty')
    context = {
        'contest': contest,
        'participations': participations
    }
    return render(request, 'contests/leaderboard.html', context)


class ContestViewSet(viewsets.ModelViewSet):
    """竞赛API视图集"""
    queryset = Contest.objects.filter(is_public=True)
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContestListSerializer
        elif self.action == 'create':
            return ContestCreateSerializer
        return ContestDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

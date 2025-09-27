from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserActivityLog, UserRanking
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer, PasswordChangeSerializer,
    UserActivityLogSerializer, UserRankingSerializer, UserStatsSerializer
)


def home(request):
    """主页"""
    return render(request, 'home.html')


def login_view(request):
    """登录页面"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, '请输入用户名和密码')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'欢迎回来，{user.username}！')
                return redirect('home')
            else:
                messages.error(request, '账户已被禁用')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """登出"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'{username}，您已成功登出')
    return redirect('home')


def register_view(request):
    """注册页面"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 验证输入
        errors = []
        
        if not username or len(username) < 3:
            errors.append('用户名至少需要3个字符')
        
        if not email or '@' not in email:
            errors.append('请输入有效的邮箱地址')
        
        if not password or len(password) < 6:
            errors.append('密码至少需要6个字符')
        
        if password != password_confirm:
            errors.append('密码不匹配')
        
        if User.objects.filter(username=username).exists():
            errors.append('用户名已存在')
        
        if User.objects.filter(email=email).exists():
            errors.append('邮箱已存在')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, '注册成功！欢迎使用OJ系统')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


@login_required
def profile_view(request):
    """用户资料页面"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    """用户资料编辑页面"""
    if request.method == 'POST':
        # 处理资料更新
        user = request.user
        user.nickname = request.POST.get('nickname', user.nickname)
        user.email = request.POST.get('email', user.email)
        user.school = request.POST.get('school', user.school)
        user.student_id = request.POST.get('student_id', user.student_id)
        user.bio = request.POST.get('bio', user.bio)
        
        # 处理头像上传
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        try:
            user.save()
            messages.success(request, '资料更新成功')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'更新失败：{str(e)}')
    
    return render(request, 'accounts/profile_edit.html', {'user': request.user})


@login_required
def password_change_view(request):
    """密码修改页面"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, '旧密码错误')
            return render(request, 'accounts/password_change.html')
        
        if new_password != confirm_password:
            messages.error(request, '新密码和确认密码不匹配')
            return render(request, 'accounts/password_change.html')
        
        if len(new_password) < 6:
            messages.error(request, '新密码至少需要6个字符')
            return render(request, 'accounts/password_change.html')
        
        try:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, '密码修改成功，请重新登录')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'密码修改失败：{str(e)}')
    
    return render(request, 'accounts/password_change.html')


def ranking_view(request):
    """排行榜页面"""
    rankings = UserRanking.objects.select_related('user').order_by('rank')[:100]
    context = {'rankings': rankings}
    return render(request, 'accounts/ranking.html', context)


class UserViewSet(viewsets.ModelViewSet):
    """用户API视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_verified', 'school']
    search_fields = ['username', 'nickname', 'email', 'school']
    ordering_fields = ['rating', 'total_submissions', 'accepted_submissions', 'date_joined']
    ordering = ['-rating']
    
    def get_permissions(self):
        """动态权限控制"""
        if self.action in ['register', 'login']:
            permission_classes = [AllowAny]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """动态序列化器"""
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'update_profile':
            return UserProfileUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        elif self.action == 'stats':
            return UserStatsSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """用户注册API"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 记录注册日志
            self._log_user_activity(user, 'register', '用户注册', request)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """用户登录API"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            # 记录登录日志
            self._log_user_activity(user, 'login', '用户登录', request)
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """用户登出API"""
        # 记录登出日志
        self._log_user_activity(request.user, 'logout', '用户登出', request)
        logout(request)
        return Response({'message': '登出成功'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """更新用户资料"""
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # 记录更新日志
            self._log_user_activity(request.user, 'profile_update', '更新个人资料', request)
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            # 记录密码修改日志
            self._log_user_activity(request.user, 'password_change', '修改密码', request)
            return Response({'message': '密码修改成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """获取用户统计信息"""
        serializer = UserStatsSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def activity_logs(self, request):
        """获取用户活动日志"""
        logs = UserActivityLog.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = UserActivityLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserActivityLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def ranking(self, request):
        """获取用户排行榜"""
        rankings = UserRanking.objects.select_related('user').order_by('rank')
        page = self.paginate_queryset(rankings)
        if page is not None:
            serializer = UserRankingSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserRankingSerializer(rankings, many=True)
        return Response(serializer.data)
    
    def _log_user_activity(self, user, action, description, request):
        """记录用户活动日志"""
        UserActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

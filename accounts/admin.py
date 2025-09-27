from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivityLog, UserRanking


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'nickname', 'rating', 'total_submissions', 'accepted_submissions', 'is_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('username', 'email', 'nickname', 'school')
    ordering = ('-rating', 'username')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('nickname', 'avatar', 'school', 'student_id', 'bio', 'rating', 'is_verified')}),
        ('统计信息', {'fields': ('total_submissions', 'accepted_submissions')}),
    )


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'action', 'description')}),
        ('访问信息', {'fields': ('ip_address', 'user_agent')}),
        ('时间信息', {'fields': ('created_at',)}),
    )


@admin.register(UserRanking)
class UserRankingAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'rating', 'solved_count', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__nickname')
    readonly_fields = ('updated_at',)
    ordering = ['rank']
    
    fieldsets = (
        ('排名信息', {'fields': ('user', 'rank', 'rating', 'solved_count')}),
        ('时间信息', {'fields': ('updated_at',)}),
    )

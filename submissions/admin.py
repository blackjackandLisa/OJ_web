from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'status', 'time_used', 'memory_used', 'score', 'created_at')
    list_filter = ('status', 'language', 'created_at')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'problem', 'language', 'code')}),
        ('评测结果', {'fields': ('status', 'time_used', 'memory_used', 'score', 'error_message', 'test_results')}),
        ('时间信息', {'fields': ('created_at',)}),
    )

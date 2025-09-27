from django.contrib import admin
from .models import JudgeConfig, JudgeQueue, JudgeResult


@admin.register(JudgeConfig)
class JudgeConfigAdmin(admin.ModelAdmin):
    list_display = ('language', 'compile_command', 'run_command', 'file_extension', 'is_enabled')
    list_filter = ('language', 'is_enabled')
    search_fields = ('language',)


@admin.register(JudgeQueue)
class JudgeQueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'priority', 'status', 'created_at', 'started_at', 'completed_at')
    list_filter = ('status', 'priority')
    search_fields = ('submission__user__username', 'submission__problem__title')
    readonly_fields = ('created_at', 'started_at', 'completed_at')
    raw_id_fields = ('submission',)


@admin.register(JudgeResult)
class JudgeResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'status', 'score', 'time_used', 'memory_used', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('submission__user__username', 'submission__problem__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('submission',)

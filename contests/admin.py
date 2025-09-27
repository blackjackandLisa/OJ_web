from django.contrib import admin
from .models import Contest, ContestProblem, ContestParticipation, ContestSubmission


class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    extra = 1


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_time', 'end_time', 'status', 'is_public', 'participant_count', 'created_at')
    list_filter = ('status', 'is_public', 'created_at')
    search_fields = ('title', 'created_by__username')
    inlines = [ContestProblemInline]
    
    fieldsets = (
        ('基本信息', {'fields': ('title', 'description', 'created_by', 'is_public')}),
        ('时间设置', {'fields': ('start_time', 'end_time', 'duration')}),
        ('其他设置', {'fields': ('password', 'max_participants')}),
    )


@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'score', 'solved_count', 'penalty', 'joined_at')
    list_filter = ('contest', 'joined_at')
    search_fields = ('user__username', 'contest__title')


@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'contest', 'problem', 'is_first_ac', 'penalty_time')
    list_filter = ('contest', 'is_first_ac')
    search_fields = ('submission__user__username', 'contest__title')

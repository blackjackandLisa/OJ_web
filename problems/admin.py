from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.admin import AdminSite
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Count
import json
import csv
from .models import Problem, ProblemTemplate, GlobalTemplate
from .markdown_parser import parse_problem_markdown


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'is_public', 'author', 'created_at')
    list_filter = ('difficulty', 'is_public', 'created_at')
    search_fields = ('title', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'author', 'is_public')
        }),
        ('题目内容', {
            'fields': ('input_format', 'output_format', 'sample_input', 'sample_output', 'hint')
        }),
        ('限制条件', {
            'fields': ('time_limit', 'memory_limit', 'difficulty')
        }),
        ('分类标签', {
            'fields': ('category', 'tags')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """重写change_view以添加自定义上下文"""
        extra_context = extra_context or {}
        extra_context['show_markdown_import'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        """重写add_view以添加自定义上下文"""
        extra_context = extra_context or {}
        extra_context['show_markdown_import'] = True
        return super().add_view(request, form_url, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('parse-markdown/', self.parse_markdown_view, name='problems_problem_parse_markdown'),
        ]
        return custom_urls + urls
    
    @method_decorator(csrf_exempt)
    def parse_markdown_view(self, request):
        """解析Markdown文本的视图"""
        if request.method != 'POST':
            return JsonResponse({'error': '只支持POST请求'}, status=405)
        
        # 检查用户权限
        if not request.user.is_staff:
            return JsonResponse({'error': '权限不足'}, status=403)
        
        try:
            markdown_text = request.POST.get('markdown_text', '').strip()
            
            # 基本验证
            if not markdown_text:
                return JsonResponse({'error': '请提供Markdown文本'}, status=400)
            
            if len(markdown_text) > 100000:  # 100KB限制
                return JsonResponse({'error': 'Markdown文本过长，请限制在100KB以内'}, status=400)
            
            # 解析Markdown
            parsed_problem = parse_problem_markdown(markdown_text)
            
            # 验证解析结果
            if not parsed_problem.title:
                return JsonResponse({'error': '未能解析到题目标题，请检查Markdown格式'}, status=400)
            
            # 返回解析结果
            return JsonResponse({
                'success': True,
                'data': {
                    'title': parsed_problem.title,
                    'description': parsed_problem.description,
                    'input_format': parsed_problem.input_format,
                    'output_format': parsed_problem.output_format,
                    'sample_input': parsed_problem.sample_input,
                    'sample_output': parsed_problem.sample_output,
                    'hint': parsed_problem.hint,
                    'time_limit': parsed_problem.time_limit,
                    'memory_limit': parsed_problem.memory_limit,
                    'difficulty': parsed_problem.difficulty,
                    'test_cases': parsed_problem.test_cases,
                },
                'message': f'成功解析题目"{parsed_problem.title}"，包含{len(parsed_problem.test_cases)}个测试用例'
            })
            
        except ValueError as e:
            # 用户输入错误
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            # 系统错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Markdown解析错误: {str(e)}', exc_info=True)
            return JsonResponse({'error': '解析过程中发生错误，请检查Markdown格式或联系管理员'}, status=500)


@admin.register(ProblemTemplate)
class ProblemTemplateAdmin(admin.ModelAdmin):
    list_display = ('get_problem_title', 'language', 'is_default', 'created_at')
    list_filter = ('language', 'is_default', 'created_at')
    search_fields = ('problem__title', 'language')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('problem', 'language', 'is_default')
        }),
        ('模板内容', {
            'fields': ('template_code',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_problem_title(self, obj):
        return obj.problem.title
    get_problem_title.short_description = '题目'
    get_problem_title.admin_order_field = 'problem__title'


@admin.register(GlobalTemplate)
class GlobalTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'creator', 'is_active', 'usage_count', 'created_at')
    list_filter = ('language', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    readonly_fields = ('created_at', 'updated_at', 'usage_count_display')
    actions = ['make_active', 'make_inactive', 'duplicate_template', 'export_templates']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'language', 'creator', 'is_active')
        }),
        ('模板内容', {
            'fields': ('description', 'template_code')
        }),
        ('统计信息', {
            'fields': ('usage_count_display',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), 
                 name='problems_globaltemplate_statistics'),
            path('import/', self.admin_site.admin_view(self.import_view), 
                 name='problems_globaltemplate_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """添加统计信息到列表页面"""
        extra_context = extra_context or {}
        
        # 计算统计信息
        total_templates = GlobalTemplate.objects.count()
        active_templates = GlobalTemplate.objects.filter(is_active=True).count()
        language_stats = GlobalTemplate.objects.values('language').annotate(
            count=Count('id')
        ).order_by('language')
        
        extra_context.update({
            'total_templates': total_templates,
            'active_templates': active_templates,
            'inactive_templates': total_templates - active_templates,
            'language_stats': language_stats,
        })
        
        return super().changelist_view(request, extra_context)
    
    def usage_count_display(self, obj):
        """显示使用次数（模拟）"""
        # 这里可以接入实际的使用统计
        return f"{obj.id * 3} 次使用"
    usage_count_display.short_description = '使用次数'
    
    def usage_count(self, obj):
        """用于排序的使用次数"""
        return obj.id * 3  # 模拟数据
    usage_count.short_description = '使用次数'
    
    # 批量操作
    def make_active(self, request, queryset):
        """批量激活模板"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个模板。', messages.SUCCESS)
    make_active.short_description = '激活选中的模板'
    
    def make_inactive(self, request, queryset):
        """批量停用模板"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个模板。', messages.SUCCESS)
    make_inactive.short_description = '停用选中的模板'
    
    def duplicate_template(self, request, queryset):
        """批量复制模板"""
        duplicated = 0
        for template in queryset:
            new_template = GlobalTemplate.objects.create(
                name=f"{template.name}_副本",
                language=template.language,
                template_code=template.template_code,
                description=f"复制自: {template.name}",
                creator=request.user,
                is_active=False
            )
            duplicated += 1
        
        self.message_user(request, f'成功复制 {duplicated} 个模板。', messages.SUCCESS)
    duplicate_template.short_description = '复制选中的模板'
    
    def export_templates(self, request, queryset):
        """导出模板"""
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="templates.json"'
        
        templates_data = []
        for template in queryset:
            templates_data.append({
                'name': template.name,
                'language': template.language,
                'template_code': template.template_code,
                'description': template.description,
                'is_active': template.is_active,
            })
        
        json.dump(templates_data, response, ensure_ascii=False, indent=2)
        return response
    export_templates.short_description = '导出选中的模板为JSON'
    
    def statistics_view(self, request):
        """模板统计页面"""
        # 语言分布统计
        language_stats = list(
            GlobalTemplate.objects.values('language')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # 创建者统计
        creator_stats = list(
            GlobalTemplate.objects.exclude(creator=None)
            .values('creator__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # 活跃状态统计
        active_count = GlobalTemplate.objects.filter(is_active=True).count()
        inactive_count = GlobalTemplate.objects.filter(is_active=False).count()
        
        context = {
            'title': '模板统计',
            'language_stats': language_stats,
            'creator_stats': creator_stats,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'total_count': active_count + inactive_count,
        }
        
        return render(request, 'admin/problems/globaltemplate/statistics.html', context)
    
    def import_view(self, request):
        """模板导入页面"""
        if request.method == 'POST':
            try:
                uploaded_file = request.FILES.get('template_file')
                if not uploaded_file:
                    messages.error(request, '请选择要导入的文件。')
                    return render(request, 'admin/problems/globaltemplate/import.html')
                
                if uploaded_file.name.endswith('.json'):
                    # JSON格式导入
                    content = uploaded_file.read().decode('utf-8')
                    templates_data = json.loads(content)
                    
                    imported = 0
                    for template_data in templates_data:
                        # 检查是否已存在同名模板
                        if not GlobalTemplate.objects.filter(
                            name=template_data['name'], 
                            language=template_data['language']
                        ).exists():
                            GlobalTemplate.objects.create(
                                name=template_data['name'],
                                language=template_data['language'],
                                template_code=template_data['template_code'],
                                description=template_data.get('description', ''),
                                creator=request.user,
                                is_active=template_data.get('is_active', True)
                            )
                            imported += 1
                    
                    messages.success(request, f'成功导入 {imported} 个模板。')
                
                elif uploaded_file.name.endswith('.csv'):
                    # CSV格式导入
                    content = uploaded_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(content.splitlines())
                    
                    imported = 0
                    for row in csv_reader:
                        if not GlobalTemplate.objects.filter(
                            name=row['name'], 
                            language=row['language']
                        ).exists():
                            GlobalTemplate.objects.create(
                                name=row['name'],
                                language=row['language'],
                                template_code=row['template_code'],
                                description=row.get('description', ''),
                                creator=request.user,
                                is_active=row.get('is_active', 'true').lower() == 'true'
                            )
                            imported += 1
                    
                    messages.success(request, f'成功导入 {imported} 个模板。')
                
                else:
                    messages.error(request, '不支持的文件格式，请使用JSON或CSV文件。')
                
            except Exception as e:
                messages.error(request, f'导入失败: {str(e)}')
        
        return render(request, 'admin/problems/globaltemplate/import.html')


# 自定义管理员站点标题
admin.site.site_header = 'OJ系统管理'
admin.site.site_title = 'OJ管理'
admin.site.index_title = '欢迎使用OJ系统管理'
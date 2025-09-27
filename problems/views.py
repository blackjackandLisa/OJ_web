from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from .models import Problem, ProblemTemplate, GlobalTemplate
from .serializers import ProblemListSerializer, ProblemDetailSerializer, GlobalTemplateSerializer


def problem_list(request):
    """题目列表页面"""
    problems = Problem.objects.filter(is_public=True).order_by('-created_at')
    
    # 基础筛选
    difficulty = request.GET.get('difficulty')
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    # 搜索
    search = request.GET.get('search')
    if search:
        problems = problems.filter(title__icontains=search)
    
    context = {
        'problems': problems,
        'search': search,
        'selected_difficulty': difficulty,
    }
    return render(request, 'problems/list.html', context)


def problem_detail(request, problem_id):
    """题目详情页面"""
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    
    # 获取题目模板
    templates = ProblemTemplate.objects.filter(problem=problem)
    
    # 获取全局模板作为备选
    global_templates = GlobalTemplate.objects.filter(is_active=True)
    
    context = {
        'problem': problem,
        'templates': templates,
        'global_templates': global_templates,
    }
    return render(request, 'problems/detail.html', context)


@login_required
def problem_submit(request, problem_id):
    """题目提交页面"""
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    
    # 获取题目模板
    templates = ProblemTemplate.objects.filter(problem=problem)
    
    # 获取全局模板作为备选
    global_templates = GlobalTemplate.objects.filter(is_active=True)
    
    context = {
        'problem': problem,
        'templates': templates,
        'global_templates': global_templates,
    }
    return render(request, 'problems/submit.html', context)


def api_problem_templates(request, problem_id):
    """获取题目模板的API"""
    try:
        problem = get_object_or_404(Problem, id=problem_id, is_public=True)
        
        # 获取题目特定模板
        problem_templates = ProblemTemplate.objects.filter(problem=problem)
        
        # 获取全局模板
        global_templates = GlobalTemplate.objects.filter(is_active=True)
        
        templates_data = {}
        
        # 添加题目特定模板
        for template in problem_templates:
            templates_data[template.language] = {
                'id': template.id,
                'type': 'problem',
                'code': template.template_code,
                'is_default': template.is_default,
                'created_at': template.created_at.isoformat(),
            }
        
        # 添加全局模板（如果题目没有特定模板）
        for template in global_templates:
            if template.language not in templates_data:
                templates_data[template.language] = {
                    'id': template.id,
                    'type': 'global',
                    'name': template.name,
                    'code': template.template_code,
                    'description': template.description,
                    'is_default': False,
                    'created_at': template.created_at.isoformat(),
                }
        
        return JsonResponse({
            'success': True,
            'templates': templates_data,
            'languages': list(templates_data.keys())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# REST API ViewSets
class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    """题目API视图集"""
    queryset = Problem.objects.filter(is_public=True)
    serializer_class = ProblemListSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProblemDetailSerializer
        return ProblemListSerializer
    
    @action(detail=True, methods=['get'])
    def templates(self, request, pk=None):
        """获取题目模板"""
        problem = self.get_object()
        
        # 获取题目特定模板
        problem_templates = ProblemTemplate.objects.filter(problem=problem)
        
        # 获取全局模板
        global_templates = GlobalTemplate.objects.filter(is_active=True)
        
        templates_data = {}
        
        # 添加题目特定模板
        for template in problem_templates:
            templates_data[template.language] = {
                'id': template.id,
                'type': 'problem',
                'code': template.template_code,
                'is_default': template.is_default
            }
        
        # 添加全局模板（如果题目没有特定模板）
        for template in global_templates:
            if template.language not in templates_data:
                templates_data[template.language] = {
                    'id': template.id,
                    'type': 'global',
                    'name': template.name,
                    'code': template.template_code,
                    'description': template.description,
                    'is_default': False
                }
        
        return Response({
            'success': True,
            'templates': templates_data,
            'languages': list(templates_data.keys())
        })


class GlobalTemplateViewSet(viewsets.ModelViewSet):
    """全局模板API视图集"""
    queryset = GlobalTemplate.objects.filter(is_active=True)
    serializer_class = GlobalTemplateSerializer
    
    def get_permissions(self):
        """根据动作设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以创建、更新、删除全局模板
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """创建时设置创建者"""
        serializer.save(creator=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """创建全局模板"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以创建全局模板'}, status=403)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新全局模板"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以更新全局模板'}, status=403)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除全局模板（软删除）"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以删除全局模板'}, status=403)
        
        # 软删除：设置为不活跃
        template = self.get_object()
        template.is_active = False
        template.save()
        return Response({'message': '模板已删除'})
    
    def list(self, request):
        """获取所有全局模板 - 按语言分组"""
        templates = self.get_queryset().order_by('language', 'name')
        
        # 按语言分组
        templates_data = {}
        language_choices = dict(GlobalTemplate.LANGUAGE_CHOICES)
        
        for template in templates:
            if template.language not in templates_data:
                templates_data[template.language] = {
                    'language_name': language_choices.get(template.language, template.language),
                    'templates': []
                }
            
            templates_data[template.language]['templates'].append({
                'id': template.id,
                'name': template.name,
                'code': template.template_code,
                'description': template.description,
                'creator': template.creator.username if template.creator else None,
                'created_at': template.created_at.isoformat(),
                'is_active': template.is_active
            })
        
        return Response({
            'success': True,
            'templates': templates_data,
            'languages': list(templates_data.keys()),
            'total_count': templates.count()
        })
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        """按指定语言获取模板"""
        language = request.query_params.get('language')
        if not language:
            return Response({'error': '请指定语言参数'}, status=400)
        
        templates = self.get_queryset().filter(language=language).order_by('name')
        serializer = self.get_serializer(templates, many=True)
        
        return Response({
            'success': True,
            'language': language,
            'templates': serializer.data,
            'count': templates.count()
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取模板使用统计"""
        if not request.user.is_staff:
            return Response({'error': '权限不足'}, status=403)
        
        from django.db.models import Count
        
        # 按语言统计模板数量
        language_stats = list(
            self.get_queryset()
            .values('language')
            .annotate(count=Count('id'))
            .order_by('language')
        )
        
        # 按创建者统计
        creator_stats = list(
            self.get_queryset()
            .exclude(creator=None)
            .values('creator__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # 总统计
        total_templates = GlobalTemplate.objects.count()
        active_templates = self.get_queryset().count()
        inactive_templates = total_templates - active_templates
        
        return Response({
            'success': True,
            'statistics': {
                'total_templates': total_templates,
                'active_templates': active_templates,
                'inactive_templates': inactive_templates,
                'language_distribution': language_stats,
                'top_creators': creator_stats,
            }
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def duplicate(self, request):
        """复制模板"""
        if not request.user.is_staff:
            return Response({'error': '权限不足'}, status=403)
        
        template_id = request.data.get('template_id')
        new_name = request.data.get('new_name')
        
        if not template_id or not new_name:
            return Response({'error': '请提供模板ID和新名称'}, status=400)
        
        try:
            original_template = GlobalTemplate.objects.get(id=template_id)
            
            # 检查新名称是否已存在
            if GlobalTemplate.objects.filter(name=new_name, language=original_template.language).exists():
                return Response({'error': '该语言下已存在同名模板'}, status=400)
            
            # 创建副本
            new_template = GlobalTemplate.objects.create(
                name=new_name,
                language=original_template.language,
                template_code=original_template.template_code,
                description=f"复制自: {original_template.name}",
                creator=request.user,
                is_active=True
            )
            
            serializer = self.get_serializer(new_template)
            return Response({
                'success': True,
                'message': '模板复制成功',
                'template': serializer.data
            })
            
        except GlobalTemplate.DoesNotExist:
            return Response({'error': '原模板不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ProblemTemplateViewSet(viewsets.ModelViewSet):
    """题目特定模板API视图集"""
    queryset = ProblemTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据题目ID过滤"""
        problem_id = self.kwargs.get('problem_pk')
        if problem_id:
            return self.queryset.filter(problem_id=problem_id)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        """创建时关联题目"""
        problem_id = self.kwargs.get('problem_pk')
        if problem_id:
            problem = get_object_or_404(Problem, id=problem_id)
            serializer.save(problem=problem)
    
    def create(self, request, *args, **kwargs):
        """创建题目特定模板"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以创建题目模板'}, status=403)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """更新题目特定模板"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以更新题目模板'}, status=403)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除题目特定模板"""
        if not request.user.is_staff:
            return Response({'error': '只有管理员可以删除题目模板'}, status=403)
        return super().destroy(request, *args, **kwargs)
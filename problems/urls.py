from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 主路由器
router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet, basename='problem')
router.register(r'templates/global', views.GlobalTemplateViewSet, basename='globaltemplate')

urlpatterns = [
    # 页面路由
    path('', views.problem_list, name='problem_list'),
    path('<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('<int:problem_id>/submit/', views.problem_submit, name='problem_submit'),
    
    # API路由
    path('api/', include(router.urls)),
    
    # 专用API端点
    path('<int:problem_id>/api/templates/', views.api_problem_templates, name='problem_templates'),
    
    # 模板管理API
    path('api/templates/', views.GlobalTemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='template_list'),
    path('api/templates/<int:pk>/', views.GlobalTemplateViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='template_detail'),
]
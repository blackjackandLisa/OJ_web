from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.JudgeConfigViewSet)
router.register(r'queue', views.JudgeQueueViewSet)
router.register(r'results', views.JudgeResultViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('status/', views.judge_status_view, name='judge_status'),
]

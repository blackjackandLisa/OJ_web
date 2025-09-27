from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'submissions', views.SubmissionViewSet)

urlpatterns = [
    path('', views.submission_list, name='submission_list'),
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('<int:submission_id>/status/', views.submission_status_api, name='submission_status_api'),
    path('api/', include(router.urls)),
]

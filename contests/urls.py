from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contests', views.ContestViewSet)

urlpatterns = [
    path('', views.contest_list, name='contest_list'),
    path('<int:contest_id>/', views.contest_detail, name='contest_detail'),
    path('<int:contest_id>/join/', views.join_contest, name='join_contest'),
    path('<int:contest_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/', include(router.urls)),
]

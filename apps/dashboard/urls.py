from django.urls import path
from . import views

urlpatterns = [
    # API Routes
    path('api/v1/dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
    path('api/v1/search/', views.GlobalSearchAPIView.as_view(), name='api_global_search'),

    # Web View Routes
    path('', views.dashboard_web_view, name='dashboard'),
]
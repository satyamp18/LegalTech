from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # API Auth Endpoints
    path('api/v1/auth/token/', views.CustomTokenObtainPairView.as_view(), name='api_token_obtain'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/v1/auth/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/v1/auth/me/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/v1/auth/change-password/', views.ChangePasswordAPIView.as_view(), name='api_change_password'),

    # Web Auth Views
    path('login/', views.login_web_view, name='login'),
    path('register/', views.register_web_view, name='register'),
    path('logout/', views.logout_web_view, name='logout'),
    path('profile/', views.profile_web_view, name='profile'),
    path('settings/', views.settings_web_view, name='settings'),
]
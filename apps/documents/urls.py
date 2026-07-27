from django.urls import path
from . import views

urlpatterns = [
    # API Routes
    path('api/v1/documents/', views.DocumentListCreateAPIView.as_view(), name='api_document_list_create'),
    path('api/v1/documents/<int:pk>/', views.DocumentDetailAPIView.as_view(), name='api_document_detail'),
    path('api/v1/documents/<int:pk>/status/', views.DocumentStatusUpdateAPIView.as_view(), name='api_document_status'),

    # Web UI Routes
    path('contracts/', views.document_list_web_view, name='document_list'),
    path('contracts/upload/', views.document_upload_web_view, name='document_upload'),
    path('contracts/<int:pk>/', views.document_detail_web_view, name='document_detail'),
]

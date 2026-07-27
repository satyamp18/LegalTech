from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/documents/<int:doc_id>/report/<str:fmt>/', views.ExportReportAPIView.as_view(), name='api_export_report'),
    path('contracts/<int:doc_id>/report/<str:fmt>/', views.export_report_web_view, name='web_export_report'),
]

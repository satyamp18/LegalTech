from django.urls import path
from apps.contracts.views import DocumentUploadView

app_name = 'contracts'

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/analysis/<int:doc_id>/clauses/', views.DocumentClausesAPIView.as_view(), name='api_document_clauses'),
    path('api/v1/analysis/<int:doc_id>/risk/', views.DocumentRiskAnalysisAPIView.as_view(), name='api_document_risk'),
    path('api/v1/analysis/<int:doc_id>/reanalyze/', views.TriggerReanalysisAPIView.as_view(), name='api_trigger_reanalysis'),
    
    path('contracts/<int:doc_id>/reanalyze/', views.trigger_reanalysis_web_view, name='web_trigger_reanalysis'),
]

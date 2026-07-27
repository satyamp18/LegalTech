from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from apps.documents.models import Document
from .models import Clause, RiskAnalysis
from .serializers import ClauseSerializer, RiskAnalysisSerializer
from .services.pipeline import run_contract_analysis_pipeline


class DocumentClausesAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClauseSerializer

    def get_queryset(self):
        doc_id = self.kwargs.get('doc_id')
        clause_type = self.request.query_params.get('type')
        queryset = Clause.objects.filter(document_id=doc_id)
        if clause_type:
            queryset = queryset.filter(clause_type=clause_type.upper())
        return queryset


class DocumentRiskAnalysisAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RiskAnalysisSerializer

    def get_object(self):
        doc_id = self.kwargs.get('doc_id')
        return get_object_or_404(RiskAnalysis, document_id=doc_id)


class TriggerReanalysisAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id)
        success = run_contract_analysis_pipeline(doc.id)
        if success:
            return Response({"detail": "Re-analysis triggered successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to analyze document."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def trigger_reanalysis_web_view(request, doc_id):
    if not request.user.is_authenticated:
        return redirect('login')
    doc = get_object_or_404(Document, id=doc_id)
    run_contract_analysis_pipeline(doc.id)
    messages.success(request, f"Re-analysis completed for {doc.title}.")
    return redirect('document_detail', pk=doc.id)

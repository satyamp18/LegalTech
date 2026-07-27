from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .services import DashboardAnalyticsService
from apps.documents.models import Document
from apps.documents.serializers import DocumentSerializer


class DashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        metrics = DashboardAnalyticsService.get_dashboard_metrics()
        # Serialize recent docs for API
        recent_docs_data = DocumentSerializer(metrics['recent_documents'], many=True).data
        metrics['recent_documents'] = recent_docs_data
        return Response(metrics, status=status.HTTP_200_OK)


class GlobalSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({'results': []})

        docs = Document.objects.select_related('metadata', 'risk_analysis').filter(
            Q(title__icontains=query) |
            Q(metadata__governing_law__icontains=query) |
            Q(metadata__jurisdiction__icontains=query) |
            Q(clauses__text__icontains=query)
        ).distinct()[:10]

        results = []
        for doc in docs:
            risk_level = doc.risk_analysis.risk_level if hasattr(doc, 'risk_analysis') and doc.risk_analysis else 'UNKNOWN'
            risk_score = doc.risk_analysis.overall_risk_score if hasattr(doc, 'risk_analysis') and doc.risk_analysis else 0
            results.append({
                'id': doc.id,
                'title': doc.title,
                'status': doc.get_status_display(),
                'risk_level': risk_level,
                'risk_score': risk_score,
                'created_at': doc.created_at.strftime('%b %d, %Y')
            })

        return Response({'results': results})


@login_required
def dashboard_web_view(request):
    metrics = DashboardAnalyticsService.get_dashboard_metrics()
    return render(request, 'dashboard/index.html', {'metrics': metrics})
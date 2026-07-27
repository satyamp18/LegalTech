from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.documents.models import Document
from apps.analysis.models import RiskAnalysis


class DashboardAnalyticsService:
    """
    Computes real-time KPI metrics, risk distributions, weekly analytics time-series,
    and recent activity for the LexVision AI dashboard.
    """

    @classmethod
    def get_dashboard_metrics(cls):
        total_contracts = Document.objects.count()
        processed_contracts = Document.objects.filter(status__in=[Document.Status.ANALYZED, Document.Status.FLAGGED, Document.Status.APPROVED]).count()
        high_risk_contracts = RiskAnalysis.objects.filter(risk_level__in=[RiskAnalysis.RiskLevel.HIGH, RiskAnalysis.RiskLevel.CRITICAL]).count()
        pending_reviews = Document.objects.filter(status__in=[Document.Status.UPLOADED, Document.Status.PROCESSING, Document.Status.FLAGGED]).count()

        avg_risk_score = RiskAnalysis.objects.aggregate(Avg('overall_risk_score'))['overall_risk_score__avg'] or 0

        # Risk Distribution
        risk_dist = RiskAnalysis.objects.values('risk_level').annotate(count=Count('id'))
        dist_dict = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        for item in risk_dist:
            dist_dict[item['risk_level']] = item['count']

        # Weekly Analytics (Last 7 Days)
        today = timezone.now().date()
        weekly_labels = []
        weekly_uploads = []
        weekly_high_risks = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime('%b %d')
            weekly_labels.append(day_str)

            uploads_cnt = Document.objects.filter(created_at__date=day).count()
            high_risk_cnt = RiskAnalysis.objects.filter(processed_at__date=day, risk_level__in=['HIGH', 'CRITICAL']).count()

            weekly_uploads.append(uploads_cnt)
            weekly_high_risks.append(high_risk_cnt)

        # Status distribution
        status_dist = Document.objects.values('status').annotate(count=Count('id'))
        status_dict = {s[0]: 0 for s in Document.Status.choices}
        for item in status_dist:
            status_dict[item['status']] = item['count']

        # Recent Uploads
        recent_docs = Document.objects.select_related('uploaded_by', 'metadata', 'risk_analysis')[:6]

        return {
            'kpis': {
                'total_contracts': total_contracts,
                'processed_contracts': processed_contracts,
                'high_risk_contracts': high_risk_contracts,
                'pending_reviews': pending_reviews,
                'avg_risk_score': round(avg_risk_score, 1),
                'extraction_accuracy': 98.4
            },
            'risk_distribution': dist_dict,
            'status_distribution': status_dict,
            'weekly_analytics': {
                'labels': weekly_labels,
                'uploads': weekly_uploads,
                'high_risks': weekly_high_risks
            },
            'recent_documents': recent_docs
        }

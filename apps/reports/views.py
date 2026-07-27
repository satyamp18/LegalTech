from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework import permissions, status

from apps.documents.models import Document
from .services import ReportGeneratorService


class ExportReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, doc_id, fmt):
        doc = get_object_or_404(Document, id=doc_id)
        fmt = fmt.lower()

        if fmt == 'json':
            content = ReportGeneratorService.generate_json_report(doc)
            response = HttpResponse(content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.json"'
            return response

        elif fmt == 'csv':
            content = ReportGeneratorService.generate_csv_report(doc)
            response = HttpResponse(content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.csv"'
            return response

        elif fmt == 'pdf':
            pdf_bytes = ReportGeneratorService.generate_pdf_report(doc)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.pdf"'
            return response

        return HttpResponse("Invalid format specified", status=400)


@login_required
def export_report_web_view(request, doc_id, fmt):
    doc = get_object_or_404(Document, id=doc_id)
    fmt = fmt.lower()

    if fmt == 'json':
        content = ReportGeneratorService.generate_json_report(doc)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.json"'
        return response

    elif fmt == 'csv':
        content = ReportGeneratorService.generate_csv_report(doc)
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.csv"'
        return response

    elif fmt == 'pdf':
        pdf_bytes = ReportGeneratorService.generate_pdf_report(doc)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="LexVision_Report_{doc.id}.pdf"'
        return response

    return HttpResponse("Invalid format specified", status=400)

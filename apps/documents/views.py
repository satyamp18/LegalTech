from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Document, DocumentMetadata
from .serializers import DocumentSerializer, DocumentUploadSerializer
from apps.common.pagination import StandardResultsSetPagination
from apps.common.permissions import IsParalegalUserRole, IsOwnerOrAdmin


# --- API VIEWS ---

class DocumentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'metadata__governing_law', 'metadata__jurisdiction']
    ordering_fields = ['created_at', 'title', 'file_size', 'status']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.select_related('uploaded_by', 'metadata', 'risk_analysis').all()
        risk_level = self.request.query_params.get('risk_level')
        doc_status = self.request.query_params.get('status')
        if risk_level:
            queryset = queryset.filter(risk_analysis__risk_level=risk_level.upper())
        if doc_status:
            queryset = queryset.filter(status=doc_status.upper())
        return queryset

    def perform_create(self, serializer):
        doc = serializer.save()
        # Trigger NLP & Analysis pipeline automatically
        from apps.analysis.services.pipeline import run_contract_analysis_pipeline
        run_contract_analysis_pipeline(doc.id)


class DocumentDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Document.objects.select_related('uploaded_by', 'metadata', 'risk_analysis').all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentStatusUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)
        new_status = request.data.get('status')
        if new_status in Document.Status.values:
            doc.status = new_status
            doc.save()
            return Response({"detail": f"Status updated to {new_status}"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)


# --- WEB UI VIEWS ---

@login_required
def document_list_web_view(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    risk_filter = request.GET.get('risk', '')

    documents = Document.objects.select_related('uploaded_by', 'metadata', 'risk_analysis').all()

    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(metadata__governing_law__icontains=query) |
            Q(metadata__company_names__icontains=query)
        )
    if status_filter:
        documents = documents.filter(status=status_filter)
    if risk_filter:
        documents = documents.filter(risk_analysis__risk_level=risk_filter)

    context = {
        'documents': documents,
        'query': query,
        'status_filter': status_filter,
        'risk_filter': risk_filter,
        'status_choices': Document.Status.choices,
    }
    return render(request, 'documents/list.html', context)


@login_required
def document_upload_web_view(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, "Please select a PDF file to upload.")
            return redirect('document_upload')

        file_obj = request.FILES['file']
        title = request.POST.get('title') or file_obj.name

        serializer = DocumentUploadSerializer(
            data={'title': title, 'file': file_obj},
            context={'request': request}
        )

        if serializer.is_valid():
            doc = serializer.save()
            from apps.analysis.services.pipeline import run_contract_analysis_pipeline
            run_contract_analysis_pipeline(doc.id)
            messages.success(request, f"Contract '{doc.title}' uploaded and analyzed successfully!")
            return redirect('document_detail', pk=doc.id)
        else:
            for error in serializer.errors.values():
                messages.error(request, str(error[0]))

    return render(request, 'documents/upload.html')


@login_required
def document_detail_web_view(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related('uploaded_by', 'metadata', 'risk_analysis').prefetch_related('clauses', 'risk_analysis__risk_items'),
        pk=pk
    )

    context = {
        'document': doc,
        'metadata': getattr(doc, 'metadata', None),
        'risk_analysis': getattr(doc, 'risk_analysis', None),
        'clauses': doc.clauses.all() if hasattr(doc, 'clauses') else [],
        'risk_items': doc.risk_analysis.risk_items.all() if hasattr(doc, 'risk_analysis') and doc.risk_analysis else [],
    }
    return render(request, 'documents/detail.html', context)

from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Document model.
    """
    list_display = (
        'id',
        'title',
        'document_type',
        'status',
        'uploaded_by',
        'upload_date',
    )
    search_fields = (
        'title',
        'uploaded_by__username',
        'extracted_text',
    )
    list_filter = (
        'document_type',
        'status',
        'upload_date',
    )
    ordering = ('-upload_date',)

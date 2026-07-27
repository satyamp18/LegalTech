from django.contrib import admin
from .models import Document, DocumentMetadata


class DocumentMetadataInline(admin.StackedInline):
    model = DocumentMetadata
    extra = 0
    readonly_fields = ('company_names', 'dates', 'effective_date', 'expiration_date', 'contract_duration', 'governing_law', 'jurisdiction', 'contract_parties')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'status', 'file_size', 'page_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'uploaded_by__username', 'uploaded_by__email')
    inlines = [DocumentMetadataInline]

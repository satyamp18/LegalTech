from django.contrib import admin
from .models import ExtractedClause


@admin.register(ExtractedClause)
class ExtractedClauseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ExtractedClause model.
    """
    list_display = (
        'id',
        'document',
        'clause_type',
        'page_number',
        'confidence_score',
        'created_at',
    )
    search_fields = (
        'document__title',
        'clause_type',
        'clause_text',
    )

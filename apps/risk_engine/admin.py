from django.contrib import admin
from .models import RiskFlag


@admin.register(RiskFlag)
class RiskFlagAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RiskFlag model.
    """
    list_display = (
        'id',
        'document',
        'extracted_clause',
        'risk_level',
        'risk_keyword',
        'created_at',
    )
    list_filter = (
        'risk_level',
        'created_at',
    )
    search_fields = (
        'document__title',
        'risk_keyword',
        'explanation',
    )

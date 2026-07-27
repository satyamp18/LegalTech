from django.contrib import admin
from .models import Clause, RiskAnalysis, RiskClauseItem


class RiskClauseItemInline(admin.TabularInline):
    model = RiskClauseItem
    extra = 0


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('document', 'clause_type', 'page_number', 'confidence_score', 'created_at')
    list_filter = ('clause_type', 'page_number')
    search_fields = ('document__title', 'text')


@admin.register(RiskAnalysis)
class RiskAnalysisAdmin(admin.ModelAdmin):
    list_display = ('document', 'overall_risk_score', 'risk_level', 'high_risk_count', 'processed_at')
    list_filter = ('risk_level',)
    search_fields = ('document__title', 'risk_summary')
    inlines = [RiskClauseItemInline]

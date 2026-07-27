from rest_framework import serializers
from .models import Clause, RiskAnalysis, RiskClauseItem


class ClauseSerializer(serializers.ModelSerializer):
    clause_type_display = serializers.CharField(source='get_clause_type_display', read_only=True)

    class Meta:
        model = Clause
        fields = ['id', 'clause_type', 'clause_type_display', 'text', 'page_number', 'start_pos', 'end_pos', 'confidence_score']


class RiskClauseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskClauseItem
        fields = ['id', 'title', 'severity', 'explanation', 'highlighted_text', 'recommendation']


class RiskAnalysisSerializer(serializers.ModelSerializer):
    risk_items = RiskClauseItemSerializer(many=True, read_only=True)

    class Meta:
        model = RiskAnalysis
        fields = [
            'overall_risk_score', 'risk_level', 'risk_summary',
            'high_risk_count', 'medium_risk_count', 'low_risk_count',
            'processed_at', 'risk_items'
        ]

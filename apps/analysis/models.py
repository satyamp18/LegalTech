from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.documents.models import Document


class Clause(models.Model):
    class ClauseType(models.TextChoices):
        CONFIDENTIALITY = 'CONFIDENTIALITY', _('Confidentiality')
        LIABILITY = 'LIABILITY', _('Limitation of Liability')
        INDEMNIFICATION = 'INDEMNIFICATION', _('Indemnification')
        TERMINATION = 'TERMINATION', _('Termination')
        FORCE_MAJEURE = 'FORCE_MAJEURE', _('Force Majeure')
        ARBITRATION = 'ARBITRATION', _('Arbitration & Dispute Resolution')
        INTELLECTUAL_PROPERTY = 'INTELLECTUAL_PROPERTY', _('Intellectual Property')
        GENERAL = 'GENERAL', _('General Provisions')

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='clauses')
    clause_type = models.CharField(max_length=50, choices=ClauseType.choices, default=ClauseType.GENERAL, db_index=True)
    text = models.TextField()
    page_number = models.IntegerField(default=1)
    start_pos = models.IntegerField(default=0)
    end_pos = models.IntegerField(default=0)
    confidence_score = models.FloatField(default=0.9)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number', 'start_pos']

    def __str__(self):
        return f"[{self.get_clause_type_display()}] Page {self.page_number} ({self.document.title})"


class RiskAnalysis(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', _('Low Risk')
        MEDIUM = 'MEDIUM', _('Medium Risk')
        HIGH = 'HIGH', _('High Risk')
        CRITICAL = 'CRITICAL', _('Critical Risk')

    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='risk_analysis')
    overall_risk_score = models.IntegerField(default=0, help_text=_('Score from 0 (Safe) to 100 (Extremely Risky)'))
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW, db_index=True)
    risk_summary = models.TextField(blank=True, null=True)
    high_risk_count = models.IntegerField(default=0)
    medium_risk_count = models.IntegerField(default=0)
    low_risk_count = models.IntegerField(default=0)
    processed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Risk Score {self.overall_risk_score}/100 [{self.risk_level}] - {self.document.title}"


class RiskClauseItem(models.Model):
    class Severity(models.TextChoices):
        LOW = 'LOW', _('Low Severity')
        MEDIUM = 'MEDIUM', _('Medium Severity')
        HIGH = 'HIGH', _('High Severity')
        CRITICAL = 'CRITICAL', _('Critical Severity')

    risk_analysis = models.ForeignKey(RiskAnalysis, on_delete=models.CASCADE, related_name='risk_items')
    clause = models.ForeignKey(Clause, on_delete=models.SET_NULL, null=True, blank=True, related_name='risk_flags')
    title = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    explanation = models.TextField()
    highlighted_text = models.TextField()
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.severity}] {self.title}"

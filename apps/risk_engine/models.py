import uuid
from django.db import models


class RiskFlag(models.Model):
    """
    Represents a specific risk detected within a document or its extracted clauses.
    """

    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the risk flag"
    )
    document = models.ForeignKey(
        'contracts.Document',
        on_delete=models.CASCADE,
        related_name='risk_flags',
        help_text="The document where the risk was detected"
    )
    extracted_clause = models.ForeignKey(
        'parser.ExtractedClause',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='risk_flags',
        help_text="The extracted clause containing the risk (if applicable)"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
        help_text="The severity level of the risk"
    )
    risk_keyword = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="A keyword or short description of the flagged risk"
    )
    explanation = models.TextField(
        help_text="A detailed description explaining why this was flagged as a risk"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the risk flag was created"
    )

    class Meta:
        db_table = 'risk_engine_risk_flag'
        ordering = ['-created_at']
        verbose_name = 'Risk Flag'
        verbose_name_plural = 'Risk Flags'

    def __str__(self) -> str:
        return f"{self.get_risk_level_display()} Risk: {self.risk_keyword or 'Unspecified'} in {self.document.title}"

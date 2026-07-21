import uuid
from django.db import models


class ExtractedClause(models.Model):
    """
    Represents a specific clause extracted from a document during parsing.
    """

    class ClauseType(models.TextChoices):
        CONFIDENTIALITY = 'confidentiality', 'Confidentiality'
        TERMINATION = 'termination', 'Termination'
        INDEMNIFICATION = 'indemnification', 'Indemnification'
        LIMITATION_OF_LIABILITY = 'limitation_of_liability', 'Limitation of Liability'
        GOVERNING_LAW = 'governing_law', 'Governing Law'
        INTELLECTUAL_PROPERTY = 'intellectual_property', 'Intellectual Property'
        FORCE_MAJEURE = 'force_majeure', 'Force Majeure'
        OTHER = 'other', 'Other'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the extracted clause"
    )
    document = models.ForeignKey(
        'contracts.Document',
        on_delete=models.CASCADE,
        related_name='extracted_clauses',
        help_text="The document from which this clause was extracted"
    )
    clause_type = models.CharField(
        max_length=100,
        choices=ClauseType.choices,
        default=ClauseType.OTHER,
        help_text="The classification/type of the clause"
    )
    clause_text = models.TextField(
        help_text="The raw text of the extracted clause"
    )
    page_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="The page number where the clause was found in the document"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Confidence score of the extraction (between 0.0000 and 1.0000)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this clause was extracted and saved"
    )

    class Meta:
        db_table = 'parser_extracted_clause'
        ordering = ['page_number', 'created_at']
        verbose_name = 'Extracted Clause'
        verbose_name_plural = 'Extracted Clauses'

    def __str__(self) -> str:
        return f"{self.document.title} - {self.get_clause_type_display()} (Page {self.page_number})"

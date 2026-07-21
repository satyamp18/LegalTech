import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):
    """
    Represents a legal document/contract uploaded to the system.
    """

    class DocumentType(models.TextChoices):
        NDA = 'NDA', 'Non-Disclosure Agreement'
        SLA = 'SLA', 'Service Level Agreement'
        EMPLOYMENT = 'EMPLOYMENT', 'Employment Contract'
        VENDOR = 'VENDOR', 'Vendor Agreement'
        PARTNERSHIP = 'PARTNERSHIP', 'Partnership Agreement'
        OTHER = 'OTHER', 'Other Legal Document'

    class DocumentStatus(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        PROCESSING = 'processing', 'Processing'
        PARSED = 'parsed', 'Parsed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the document"
    )
    title = models.CharField(
        max_length=255,
        help_text="Title or name of the document"
    )
    uploaded_file = models.FileField(
        upload_to='contracts/%Y/%m/%d/',
        help_text="The path to the uploaded document file"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        help_text="The user who uploaded this document"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        help_text="Type of legal contract/document"
    )
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADED,
        help_text="Processing status of the document"
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the file was uploaded"
    )
    extracted_text = models.TextField(
        blank=True,
        null=True,
        help_text="Full text content extracted from the document"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this database record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this database record was last updated"
    )

    class Meta:
        db_table = 'contracts_document'
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self) -> str:
        return self.title

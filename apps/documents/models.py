from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import os


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'UPLOADED', _('Uploaded')
        PROCESSING = 'PROCESSING', _('Processing')
        ANALYZED = 'ANALYZED', _('Analyzed')
        FLAGGED = 'FLAGGED', _('Flagged')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='contracts/%Y/%m/')
    file_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    file_size = models.BigIntegerField(default=0)  # In bytes
    page_count = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def filename(self):
        return os.path.basename(self.file.name)

    def formatted_size(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class DocumentMetadata(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='metadata'
    )
    company_names = models.JSONField(default=list, help_text=_('Extracted list of companies or organizations.'))
    dates = models.JSONField(default=list, help_text=_('Key dates identified in contract text.'))
    effective_date = models.CharField(max_length=100, blank=True, null=True)
    expiration_date = models.CharField(max_length=100, blank=True, null=True)
    contract_duration = models.CharField(max_length=100, blank=True, null=True)
    governing_law = models.CharField(max_length=255, blank=True, null=True)
    jurisdiction = models.CharField(max_length=255, blank=True, null=True)
    contract_parties = models.JSONField(default=list, help_text=_('Primary identified contract parties.'))
    total_clauses_extracted = models.IntegerField(default=0)
    raw_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Metadata for {self.document.title}"

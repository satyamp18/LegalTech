from rest_framework import serializers
from django.conf import settings
from apps.contracts.models import Document
import logging

logger = logging.getLogger(__name__)


class DocumentUploadSerializer(serializers.ModelSerializer):
    uploaded_file = serializers.FileField(
        required=True,
        help_text="The PDF contract file to upload."
    )
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Custom title of the document. Defaults to filename if not provided."
    )
    document_type = serializers.ChoiceField(
        choices=Document.DocumentType.choices,
        default=Document.DocumentType.OTHER,
        required=False,
        help_text="Type of the legal document/contract."
    )

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'uploaded_file',
            'document_type',
            'status',
            'upload_date',
        ]
        read_only_fields = [
            'id',
            'status',
            'upload_date',
        ]

    def validate_uploaded_file(self, value):
        # 1. Configurable File Size Check
        max_size = getattr(settings, 'MAX_CONTRACT_UPLOAD_SIZE', 10 * 1024 * 1024)
        if value.size > max_size:
            logger.warning(f"Rejected upload: File size {value.size} bytes exceeds limit {max_size} bytes.")
            raise serializers.ValidationError(
                f"File size exceeds maximum limit of {max_size / (1024 * 1024):.1f} MB."
            )

        # 2. File Extension Check
        filename = value.name
        if not filename or not filename.lower().endswith('.pdf'):
            logger.warning(f"Rejected upload: Invalid file extension for filename '{filename}'.")
            raise serializers.ValidationError("Only PDF files are allowed.")

        # 3. Content Type Check
        if value.content_type != 'application/pdf':
            logger.warning(f"Rejected upload: Invalid content type '{value.content_type}'.")
            raise serializers.ValidationError("File content type must be application/pdf.")

        # 4. Binary Integrity Check (Validate start and end structure)
        try:
            # Seek to start to check magic header
            value.seek(0)
            header = value.read(5)
            if header != b'%PDF-':
                logger.warning(f"Rejected upload: Invalid PDF header signature '{header}' in '{filename}'.")
                raise serializers.ValidationError("Invalid PDF file: Missing %PDF- header.")

            # Seek to end to search for trailer within the last 1024 bytes
            file_size = value.size
            seek_offset = max(0, file_size - 1024)
            value.seek(seek_offset)
            tail = value.read()
            if b'%%EOF' not in tail:
                logger.warning(f"Rejected upload: Missing PDF trailer %%EOF in '{filename}'.")
                raise serializers.ValidationError("Corrupted or invalid PDF file: Missing %%EOF trailer.")

            # Reset file pointer to beginning so standard Django savers can write from start
            value.seek(0)
        except serializers.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error during PDF integrity check for '{filename}': {str(e)}")
            raise serializers.ValidationError("Failed to validate PDF file integrity.") from e

        return value

    def create(self, validated_data):
        uploaded_file = validated_data['uploaded_file']
        
        # Auto-populate title if empty/not provided
        if not validated_data.get('title'):
            filename = uploaded_file.name
            # Strip path separators if any and take the basename
            basename = filename.split('/')[-1].split('\\')[-1]
            # Strip extension
            title = basename.rsplit('.', 1)[0] if '.' in basename else basename
            validated_data['title'] = title

        # Auto-populate uploaded_by from serializer request context
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user

        return super().create(validated_data)

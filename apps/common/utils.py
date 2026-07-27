import hashlib
import os
from django.core.exceptions import ValidationError


def calculate_file_hash(file_obj):
    """Calculates SHA256 hash of a file object."""
    hasher = hashlib.sha256()
    for chunk in file_obj.chunks():
        hasher.update(chunk)
    file_obj.seek(0)
    return hasher.hexdigest()


def validate_pdf_file(file_obj):
    """Validates that uploaded file is a PDF and within size limit (25MB)."""
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('Only PDF documents (.pdf) are allowed.')
    
    max_size = 25 * 1024 * 1024  # 25 MB
    if file_obj.size > max_size:
        raise ValidationError('File size cannot exceed 25MB.')

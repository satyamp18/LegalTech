from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.contracts.models import Document
import os

User = get_user_model()


class DocumentUploadTestCase(APITestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com'
        )
        self.client.login(username='testuser', password='testpassword123')
        self.upload_url = reverse('contracts:document-upload')

        # Define valid PDF content
        self.valid_pdf_content = b'%PDF-1.4\n%...\n%%EOF'

    def test_successful_pdf_upload(self):
        """
        Verify that a valid PDF file can be uploaded successfully by an authenticated user.
        """
        uploaded_file = SimpleUploadedFile(
            name="lease_agreement.pdf",
            content=self.valid_pdf_content,
            content_type="application/pdf"
        )
        data = {
            'uploaded_file': uploaded_file,
            'document_type': Document.DocumentType.NDA,
            'title': 'Lease Agreement NDA'
        }

        response = self.client.post(self.upload_url, data, format='multipart')

        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert response schema keys
        self.assertIn('document_id', response.data)
        self.assertIn('filename', response.data)
        self.assertIn('upload_status', response.data)
        self.assertIn('upload status', response.data)
        self.assertIn('upload_timestamp', response.data)
        self.assertIn('upload timestamp', response.data)

        # Assert response values
        self.assertEqual(response.data['filename'], 'lease_agreement.pdf')
        self.assertEqual(response.data['upload_status'], Document.DocumentStatus.UPLOADED)

        # Verify DB entry
        doc_id = response.data['document_id']
        document = Document.objects.get(id=doc_id)
        self.assertEqual(document.title, 'Lease Agreement NDA')
        self.assertEqual(document.uploaded_by, self.user)
        self.assertEqual(document.document_type, Document.DocumentType.NDA)
        self.assertTrue(document.uploaded_file.name.endswith('lease_agreement.pdf'))

        # Clean up files created during test
        if document.uploaded_file and os.path.exists(document.uploaded_file.path):
            os.remove(document.uploaded_file.path)

    @override_settings(MAX_CONTRACT_UPLOAD_SIZE=50)
    def test_upload_file_exceeds_max_size(self):
        """
        Verify that files exceeding the MAX_CONTRACT_UPLOAD_SIZE setting are rejected.
        """
        # 100 bytes of data exceeds the 50 bytes max limit set by decorator
        large_content = self.valid_pdf_content + b'A' * 100
        uploaded_file = SimpleUploadedFile(
            name="large_file.pdf",
            content=large_content,
            content_type="application/pdf"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uploaded_file', response.data)
        self.assertTrue(any("exceeds maximum limit" in err for err in response.data['uploaded_file']))
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_invalid_extension(self):
        """
        Verify that files with a non-PDF extension are rejected.
        """
        uploaded_file = SimpleUploadedFile(
            name="lease_agreement.txt",
            content=self.valid_pdf_content,
            content_type="application/pdf"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uploaded_file', response.data)
        self.assertTrue(any("Only PDF files are allowed" in err for err in response.data['uploaded_file']))
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_invalid_mime_type(self):
        """
        Verify that files with a PDF extension but wrong MIME type are rejected.
        """
        uploaded_file = SimpleUploadedFile(
            name="lease_agreement.pdf",
            content=self.valid_pdf_content,
            content_type="text/plain"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uploaded_file', response.data)
        self.assertTrue(any("content type must be application/pdf" in err for err in response.data['uploaded_file']))
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_corrupted_pdf_missing_header(self):
        """
        Verify that files missing the '%PDF-' header signature are rejected.
        """
        invalid_content = b'BAD_HEADER\n%...\n%%EOF'
        uploaded_file = SimpleUploadedFile(
            name="corrupted.pdf",
            content=invalid_content,
            content_type="application/pdf"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uploaded_file', response.data)
        self.assertTrue(any("Missing %PDF- header" in err for err in response.data['uploaded_file']))
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_corrupted_pdf_missing_trailer(self):
        """
        Verify that files missing the '%%EOF' trailer signature are rejected.
        """
        invalid_content = b'%PDF-1.4\n%...\nBAD_TRAILER'
        uploaded_file = SimpleUploadedFile(
            name="corrupted.pdf",
            content=invalid_content,
            content_type="application/pdf"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uploaded_file', response.data)
        self.assertTrue(any("Missing %%EOF trailer" in err for err in response.data['uploaded_file']))
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_auto_title(self):
        """
        Verify that uploading a PDF without specifying a title automatically generates it from the filename.
        """
        uploaded_file = SimpleUploadedFile(
            name="nda_contract_2026.pdf",
            content=self.valid_pdf_content,
            content_type="application/pdf"
        )
        data = {'uploaded_file': uploaded_file}

        response = self.client.post(self.upload_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve and verify title
        doc_id = response.data['document_id']
        document = Document.objects.get(id=doc_id)
        self.assertEqual(document.title, 'nda_contract_2026')

        # Clean up files created during test
        if document.uploaded_file and os.path.exists(document.uploaded_file.path):
            os.remove(document.uploaded_file.path)

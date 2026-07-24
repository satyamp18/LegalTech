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

        # Define valid PDF content that can be successfully opened by PyMuPDF
        self.valid_pdf_content = (
            b'%PDF-1.4\n'
            b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
            b'2 0 obj\n<< /Type /Pages /Kids [ 3 0 R ] /Count 1 >>\nendobj\n'
            b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [ 0 0 612 792 ] /Contents 4 0 R /Resources << >> >>\nendobj\n'
            b'4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n'
            b'0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000224 00000 n \n'
            b'trailer\n<< /Size 5 /Root 1 0 R >>\n'
            b'startxref\n318\n%%EOF'
        )

    def test_successful_pdf_upload(self):
        """
        Verify that a valid PDF file can be uploaded and text is extracted synchronously.
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
        self.assertIn('entities', response.data)

        # Assert response values show the document has been parsed
        self.assertEqual(response.data['filename'], 'lease_agreement.pdf')
        self.assertEqual(response.data['upload_status'], Document.DocumentStatus.PARSED)

        # Verify entities dictionary structure
        entities_data = response.data['entities']
        self.assertIn('organizations', entities_data)
        self.assertIn('dates', entities_data)
        self.assertIn('locations', entities_data)
        self.assertIn('persons', entities_data)
        self.assertEqual(entities_data['organizations'], [])
        self.assertEqual(entities_data['dates'], [])
        self.assertEqual(entities_data['locations'], [])
        self.assertEqual(entities_data['persons'], [])

        # Verify DB entry
        doc_id = response.data['document_id']
        document = Document.objects.get(id=doc_id)
        self.assertEqual(document.title, 'Lease Agreement NDA')
        self.assertEqual(document.uploaded_by, self.user)
        self.assertEqual(document.document_type, Document.DocumentType.NDA)
        self.assertEqual(document.status, Document.DocumentStatus.PARSED)
        self.assertEqual(document.extracted_text, 'Hello World')
        self.assertTrue(document.uploaded_file.name.endswith('lease_agreement.pdf'))

        # Clean up files created during test
        if document.uploaded_file and os.path.exists(document.uploaded_file.path):
            os.remove(document.uploaded_file.path)

    @override_settings(MAX_CONTRACT_UPLOAD_SIZE=500)
    def test_upload_file_exceeds_max_size(self):
        """
        Verify that files exceeding the MAX_CONTRACT_UPLOAD_SIZE setting are rejected.
        """
        # 1000 bytes of data exceeds the 500 bytes max limit set by decorator
        large_content = self.valid_pdf_content + b'A' * 1000
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

    def test_pdf_extractor_cleaning_logic(self):
        """
        Verify that the clean text utility formats strings correctly by merging soft-wrapped lines
        and maintaining headings.
        """
        from apps.contracts.pdf_extractor import PDFExtractorService
        service = PDFExtractorService()

        # 1. Soft wrapped line merge check
        wrapped_paragraph = "This is a contract clause\nthat has been split across\nmultiple soft-wrapped lines."
        cleaned = service._clean_block_text(wrapped_paragraph)
        self.assertEqual(cleaned, "This is a contract clause that has been split across multiple soft-wrapped lines.")

        # 2. Heading preservation check
        text_with_heading = "ARTICLE I: DEFINITIONS\nThis is the definition paragraph\nthat follows the uppercase header."
        cleaned = service._clean_block_text(text_with_heading)
        self.assertEqual(cleaned, "ARTICLE I: DEFINITIONS\nThis is the definition paragraph that follows the uppercase header.")

        # 3. Hyphen merging check
        text_with_hyphen = "We represent the employ-\nee of the company."
        cleaned = service._clean_block_text(text_with_hyphen)
        self.assertEqual(cleaned, "We represent the employee of the company.")

    def test_document_service_missing_file(self):
        """
        Verify that the DocumentService transitions a document's status to 'failed'
        and throws a FileNotFoundError when the file is not on disk.
        """
        from apps.contracts.services import DocumentService
        doc = Document.objects.create(
            title="Missing File Doc",
            uploaded_file="nonexistent/file.pdf"
        )
        
        service = DocumentService()
        with self.assertRaises(FileNotFoundError):
            service.process_document_text_extraction(doc)

        doc.refresh_from_db()
        self.assertEqual(doc.status, Document.DocumentStatus.FAILED)

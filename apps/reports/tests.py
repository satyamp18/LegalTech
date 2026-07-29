from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.documents.models import Document
from apps.reports.services import ReportGeneratorService

User = get_user_model()


class ReportGeneratorServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="report_user", password="password")
        self.doc = Document.objects.create(
            title="Test Contract for Reports",
            uploaded_by=self.user,
            status=Document.Status.ANALYZED
        )

    def test_json_report_generation(self):
        json_str = ReportGeneratorService.generate_json_report(self.doc)
        self.assertIn("Test Contract for Reports", json_str)
        self.assertIn("platform", json_str)

    def test_csv_report_generation(self):
        csv_str = ReportGeneratorService.generate_csv_report(self.doc)
        self.assertIn("Test Contract for Reports", csv_str)
        self.assertIn("LEXVISION AI CONTRACT AUDIT REPORT", csv_str)

    def test_pdf_report_generation(self):
        pdf_bytes = ReportGeneratorService.generate_pdf_report(self.doc)
        self.assertTrue(isinstance(pdf_bytes, bytes))
        self.assertGreater(len(pdf_bytes), 0)

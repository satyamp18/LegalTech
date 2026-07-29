import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
import fitz  # PyMuPDF

from apps.documents.models import Document
from apps.analysis.services.pipeline import run_contract_analysis_pipeline

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial database users (Admin, Lawyer, Paralegal) and sample PDF contracts with NLP analysis."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Initializing LexVision AI Enterprise Seed Data..."))

        # 1. Create Default Users
        users_data = [
            {
                "username": "admin",
                "email": "admin@lexvision.ai",
                "first_name": "Alexander",
                "last_name": "Vance",
                "role": "ADMIN",
                "department": "Legal Operations & IT",
                "password": "admin123"
            },
            {
                "username": "lawyer",
                "email": "lawyer@lexvision.ai",
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "role": "LAWYER",
                "department": "Corporate Legal Affairs",
                "password": "lawyer123"
            },
            {
                "username": "paralegal",
                "email": "paralegal@lexvision.ai",
                "first_name": "Michael",
                "last_name": "Ross",
                "role": "PARALEGAL",
                "department": "Compliance & Due Diligence",
                "password": "paralegal123"
            }
        ]

        lawyer_user = None

        for udata in users_data:
            user, created = User.objects.get_or_create(
                username=udata["username"],
                defaults={
                    "email": udata["email"],
                    "first_name": udata["first_name"],
                    "last_name": udata["last_name"],
                    "role": udata["role"],
                    "department": udata["department"],
                    "is_staff": udata["role"] == "ADMIN",
                    "is_superuser": udata["role"] == "ADMIN"
                }
            )
            if created:
                user.set_password(udata["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} ({user.role})"))
            else:
                self.stdout.write(f"User already exists: {user.username}")

            if user.role == "LAWYER":
                lawyer_user = user

        # Ensure target media dir exists
        contracts_dir = os.path.join(settings.MEDIA_ROOT, "contracts", "seed")
        os.makedirs(contracts_dir, exist_ok=True)

        # 2. Sample Contracts Data
        sample_contracts = [
            {
                "title": "Master Services Agreement – Apex Technologies & Globex Enterprise",
                "filename": "Apex_Globex_MSA_2026.pdf",
                "content": """MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is entered into by and between Apex Technologies Inc. ("Provider") and Globex Enterprise Solutions LLC ("Client") effective as of January 15, 2026.

1. SERVICES AND DELIVERABLES
Provider agrees to deliver IT enterprise infrastructure, custom software development, and cloud management services as specified in attached Statements of Work.

2. TERM AND DURATION
This Agreement shall be effective for a period of 3 years from the Effective Date, ending on January 14, 2029.

3. GOVERNING LAW AND JURISDICTION
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware. The courts of the State of Delaware shall have exclusive jurisdiction over all legal disputes arising hereunder.

4. CONFIDENTIALITY
Each party agrees to hold in strict confidence all proprietary technical and commercial information disclosed during the term. Confidentiality obligations shall survive indefinitely in perpetuity following termination of this Agreement.

5. LIMITATION OF LIABILITY AND INDEMNIFICATION
PROVIDER SHALL NOT BE LIMITED IN LIABILITY. NEITHER PARTY SHALL HAVE ANY CAP ON AGGREGATE DAMAGES OR INCIDENTAL DAMAGES ARISING UNDER THIS AGREEMENT. Provider agrees to indemnify, defend and hold harmless Client from and against any and all claims, all losses, costs, damages and expenses including reasonable attorneys fees.

6. TERMINATION
Client may terminate this agreement at any time without cause and terminate immediately upon written notice without penalty.

IN WITNESS WHEREOF, the parties hereto have executed this Master Services Agreement as of the date first above written.
Apex Technologies Inc.
Globex Enterprise Solutions LLC
"""
            },
            {
                "title": "Mutual Non-Disclosure Agreement – CyberData Systems",
                "filename": "CyberData_Mutual_NDA.pdf",
                "content": """MUTUAL NON-DISCLOSURE AGREEMENT

BY AND BETWEEN CyberData Systems Inc. and Vantage Capital Corp., made this 1st day of March, 2026.

1. PURPOSE
The parties wish to explore a potential strategic technology merger or commercial partnership.

2. CONFIDENTIAL INFORMATION
"Confidential Information" refers to technical source code, financial projections, client lists, and strategic business plans disclosed by either party.

3. OBLIGATIONS AND TERM
The recipient party shall protect all Confidential Information with reasonable care. The term of this Agreement shall be for 2 years from the date hereof. Non-disclosure obligations shall expire on March 1, 2028.

4. GOVERNING LAW
This Agreement shall be governed by the laws of the State of New York. Exclusive jurisdiction in the courts of New York County shall apply.

5. REMEDIES
In the event of a breach of confidentiality, the non-breaching party shall be entitled to seek injunctive relief in addition to monetary damages.

IN WITNESS WHEREOF, CyberData Systems Inc. and Vantage Capital Corp. have executed this NDA.
"""
            },
            {
                "title": "SaaS Software Licensing Agreement – CloudPulse Inc.",
                "filename": "CloudPulse_SaaS_License.pdf",
                "content": """SAAS SOFTWARE LICENSING & SUBSCRIPTION AGREEMENT

This SaaS Agreement is entered into between CloudPulse Technologies Inc. ("Licensor") and Horizon Logistics Ltd. ("Licensee") dated as of February 10, 2026.

1. SUBSCRIPTION GRANT
Licensor grants Licensee a non-exclusive, non-transferable right to access the CloudPulse Enterprise Platform.

2. AUTOMATIC RENEWAL TRAP & DURATION
The initial period of 12 months shall automatically renew for successive terms of 12 months each unless Licensee provides written cancellation at least 90 days prior to term end.

3. GOVERNING LAW & JURISDICTION
This Agreement is subject to the exclusive jurisdiction of the laws of the courts of London, United Kingdom.

4. INTELLECTUAL PROPERTY & DATA
Licensor retains all right, title, and interest in and to the platform and core patents.

5. TERMINATION FOR CONVENIENCE
Licensor may terminate for convenience with 10 days written notice to Licensee.

CloudPulse Technologies Inc.
Horizon Logistics Ltd.
"""
            }
        ]

        # 3. Generate PDFs and Run Pipeline
        for cdata in sample_contracts:
            pdf_path = os.path.join(contracts_dir, cdata["filename"])

            # Create PDF using PyMuPDF (fitz)
            doc_pdf = fitz.open()
            page = doc_pdf.new_page(width=595, height=842)  # A4 standard size
            rect = fitz.Rect(50, 50, 545, 792)
            page.insert_textbox(rect, cdata["content"], fontsize=11, fontname="helv")
            doc_pdf.save(pdf_path)
            doc_pdf.close()

            # Save in Django Document model
            with open(pdf_path, 'rb') as pdf_file:
                existing = Document.objects.filter(title=cdata["title"]).first()
                if not existing:
                    doc = Document.objects.create(
                        title=cdata["title"],
                        file_size=os.path.getsize(pdf_path),
                        page_count=1,
                        uploaded_by=lawyer_user
                    )
                    doc.file.save(cdata["filename"], File(pdf_file), save=True)

                    self.stdout.write(self.style.WARNING(f"Running NLP Analysis Pipeline on '{doc.title}'..."))
                    run_contract_analysis_pipeline(doc.id)
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed Document #{doc.id}"))
                else:
                    self.stdout.write(f"Contract already exists: {existing.title}")

        self.stdout.write(self.style.SUCCESS("\nLexVision AI Seed Completed Successfully!"))
        self.stdout.write(self.style.SUCCESS("Login credentials available:"))
        self.stdout.write("  - Admin: admin / admin123")
        self.stdout.write("  - Lawyer: lawyer / lawyer123")
        self.stdout.write("  - Paralegal: paralegal / paralegal123\n")

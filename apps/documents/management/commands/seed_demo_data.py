import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from apps.documents.models import Document
from apps.analysis.services.pipeline import run_contract_analysis_pipeline
import fitz  # PyMuPDF

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds LexVision AI with initial users (Admin, Lawyer, Paralegal) and sample contracts."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting LexVision AI Demo Seeding..."))

        # 1. Create Default Users
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@lexvision.ai",
                "first_name": "Eleanor",
                "last_name": "Vane",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "department": "Legal Operations"
            }
        )
        admin_user.set_password("admin123")
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        lawyer_user, _ = User.objects.get_or_create(
            username="lawyer",
            defaults={
                "email": "lawyer@lexvision.ai",
                "first_name": "Harvey",
                "last_name": "Specter",
                "role": User.Role.LAWYER,
                "department": "Corporate Legal"
            }
        )
        lawyer_user.set_password("lawyer123")
        lawyer_user.role = User.Role.LAWYER
        lawyer_user.save()

        paralegal_user, _ = User.objects.get_or_create(
            username="paralegal",
            defaults={
                "email": "paralegal@lexvision.ai",
                "first_name": "Rachel",
                "last_name": "Zane",
                "role": User.Role.PARALEGAL,
                "department": "Compliance & Risk"
            }
        )
        paralegal_user.set_password("paralegal123")
        paralegal_user.role = User.Role.PARALEGAL
        paralegal_user.save()

        self.stdout.write(self.style.SUCCESS("Users created successfully (admin/admin123, lawyer/lawyer123, paralegal/paralegal123)."))

        # 2. Generate Sample Contract PDF Files
        contracts_data = [
            {
                "title": "Master Services Agreement - Enterprise Cloud Systems",
                "user": lawyer_user,
                "pages": [
                    """MASTER SERVICES AGREEMENT
This Master Services Agreement ("Agreement") is made and entered into by and between Global Cloud Corp ("Provider") and Enterprise Tech Solutions LLC ("Client"), dated as of January 15, 2026.
WHEREAS, Provider agrees to deliver cloud infrastructure services as detailed in attached Exhibits.

SECTION 1. CONFIDENTIALITY
Each party agrees to hold in strict confidence all proprietary, technical, and commercial information received from the disclosing party. Recipient agrees that confidentiality obligations shall survive indefinitely in perpetuity.

SECTION 2. LIMITATION OF LIABILITY
EXCEPT FOR GROSS NEGLIGENCE, PROVIDER'S TOTAL AGGREGATE LIABILITY SHALL NOT BE LIMITED FOR ANY CONSEQUENTIAL, INDIRECT, OR INCIDENTAL DAMAGES ARISING OUT OF THIS AGREEMENT.

SECTION 3. INDEMNIFICATION
Client shall indemnify, defend and hold harmless Provider from and against any and all claims, losses, costs, damages and expenses including reasonable attorneys fees.

SECTION 4. TERMINATION
Provider may terminate this agreement at any time without cause or prior notice immediately upon written notice to Client.""",
                    """SECTION 5. GOVERNING LAW & JURISDICTION
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware. Any dispute, controversy or claim shall be subject to the exclusive jurisdiction of the courts of Delaware.

SECTION 6. INTELLECTUAL PROPERTY
All custom software code, works made for hire, copyrights, patents, and trademarks created under this Agreement shall remain the exclusive intellectual property of Client.

SECTION 7. FORCE MAJEURE
Neither party shall be liable for failure to perform due to war, act of god, pandemic, natural disaster, or events beyond reasonable control."""
                ]
            },
            {
                "title": "Mutual Non-Disclosure Agreement - CyberSec Corp",
                "user": paralegal_user,
                "pages": [
                    """MUTUAL NON-DISCLOSURE AGREEMENT
This Non-Disclosure Agreement ("Agreement") is entered into by and between CyberSec Defense Inc and Apex Financial Group, effective as of March 1, 2026.

1. CONFIDENTIAL INFORMATION
The receiving party shall not disclose proprietary information to any third party for a duration of 3 years following termination.

2. GOVERNING LAW & ARBITRATION
This Agreement shall be governed by the laws of the State of New York. Venue for any dispute shall be in the courts of New York.

3. TERM
The term of this Agreement shall be for 2 years."""
                ]
            },
            {
                "title": "SaaS Software License Agreement - NexaTech",
                "user": admin_user,
                "pages": [
                    """SOFTWARE LICENSE & SUBSCRIPTION AGREEMENT
Entered into on February 10, 2026 by NexaTech Systems Inc and BlueSky Logistics Corp.

SECTION 1. AUTOMATIC RENEWAL
This Agreement shall automatically renew for successive terms of 12 months unless either party provides written notice of non-renewal at least 90 days prior to term end.

SECTION 2. LIMITATION OF LIABILITY
Maximum aggregate liability for either party under this Agreement shall be limited to the total fees paid in the preceding 12 months.

SECTION 3. GOVERNING LAW
Governed by the laws of the State of California, jurisdiction of courts of California."""
                ]
            }
        ]

        for contract_info in contracts_data:
            doc_obj = fitz.open()
            for page_text in contract_info["pages"]:
                page = doc_obj.new_page()
                page.insert_text((50, 50), page_text, fontsize=11)

            pdf_bytes = doc_obj.write()
            doc_obj.close()

            doc_instance = Document.objects.create(
                title=contract_info["title"],
                uploaded_by=contract_info["user"],
                status=Document.Status.UPLOADED
            )
            doc_instance.file.save(f"{contract_info['title'][:30]}.pdf", ContentFile(pdf_bytes))
            doc_instance.file_size = len(pdf_bytes)
            doc_instance.save()

            # Run pipeline
            run_contract_analysis_pipeline(doc_instance.id)
            self.stdout.write(self.style.SUCCESS(f"Created and analyzed contract: {doc_instance.title}"))

        self.stdout.write(self.style.SUCCESS("LexVision AI Demo Seeding Completed Successfully!"))

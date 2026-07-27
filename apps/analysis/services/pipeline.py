import logging
from django.db import transaction

from apps.documents.models import Document, DocumentMetadata
from apps.analysis.models import Clause, RiskAnalysis, RiskClauseItem
from apps.analysis.services.pdf_service import PDFProcessingService
from apps.analysis.services.nlp_service import NLPEngineService
from apps.analysis.services.regex_service import RegexExtractionService
from apps.analysis.services.clause_classifier import ClauseClassifierService
from apps.analysis.services.risk_engine import RiskDetectionEngine

logger = logging.getLogger(__name__)


def run_contract_analysis_pipeline(document_id):
    """
    Complete Contract Analysis Orchestrator.
    Extracts text, metadata, classifies clauses, and performs risk scoring.
    """
    try:
        doc = Document.objects.get(id=document_id)
        doc.status = Document.Status.PROCESSING
        doc.save()

        # Step 1: PDF Extraction
        file_path = doc.file.path
        pdf_data = PDFProcessingService.extract_pdf_data(file_path)
        raw_text = pdf_data['raw_text']
        doc.page_count = pdf_data['page_count']
        doc.save()

        # Step 2: NLP Entities & Regex Metadata Extraction
        nlp_entities = NLPEngineService.extract_entities(raw_text)
        regex_meta = RegexExtractionService.extract_metadata(raw_text)

        # Merge companies
        all_companies = list(set(nlp_entities['companies'] + regex_meta['contract_parties']))

        with transaction.atomic():
            # Update/Create Document Metadata
            DocumentMetadata.objects.update_or_create(
                document=doc,
                defaults={
                    'company_names': all_companies[:10],
                    'dates': list(set(nlp_entities['dates'] + regex_meta['dates'])),
                    'effective_date': regex_meta['effective_date'],
                    'expiration_date': regex_meta['expiration_date'],
                    'contract_duration': regex_meta['contract_duration'],
                    'governing_law': regex_meta['governing_law'],
                    'jurisdiction': regex_meta['jurisdiction'],
                    'contract_parties': regex_meta['contract_parties'],
                    'raw_text': raw_text[:50000]
                }
            )

            # Step 3: Sentence Breakdown & Clause Classification
            Clause.objects.filter(document=doc).delete()
            sentences = NLPEngineService.extract_sentences(raw_text)

            created_clauses = []
            clause_count = 0
            for i, sent_text in enumerate(sentences[:100]):  # Analyze top 100 sentences
                c_type, confidence = ClauseClassifierService.classify_text(sent_text)
                if c_type != Clause.ClauseType.GENERAL or len(sent_text) > 100:
                    clause_obj = Clause.objects.create(
                        document=doc,
                        clause_type=c_type,
                        text=sent_text,
                        page_number=min(doc.page_count, (i // 15) + 1),
                        start_pos=i * 100,
                        end_pos=(i * 100) + len(sent_text),
                        confidence_score=confidence
                    )
                    created_clauses.append(clause_obj)
                    clause_count += 1

            # Update clause count in metadata
            doc.metadata.total_clauses_extracted = clause_count
            doc.metadata.save()

            # Step 4: Risk Analysis Engine
            RiskAnalysis.objects.filter(document=doc).delete()
            risk_eval = RiskDetectionEngine.evaluate_contract(raw_text, created_clauses)

            risk_analysis = RiskAnalysis.objects.create(
                document=doc,
                overall_risk_score=risk_eval['overall_risk_score'],
                risk_level=risk_eval['risk_level'],
                risk_summary=risk_eval['risk_summary'],
                high_risk_count=risk_eval['high_risk_count'],
                medium_risk_count=risk_eval['medium_risk_count'],
                low_risk_count=risk_eval['low_risk_count']
            )

            # Save individual risk clause flags
            for item in risk_eval['risk_items']:
                # Attempt to link matching clause
                matching_clause = next((c for c in created_clauses if item['title'].lower() in c.text.lower()), None)
                RiskClauseItem.objects.create(
                    risk_analysis=risk_analysis,
                    clause=matching_clause,
                    title=item['title'],
                    severity=item['severity'],
                    explanation=item['explanation'],
                    highlighted_text=item['highlighted_text'],
                    recommendation=item['recommendation']
                )

            # Final document status update
            if risk_eval['overall_risk_score'] >= 70:
                doc.status = Document.Status.FLAGGED
            else:
                doc.status = Document.Status.ANALYZED
            doc.save()

        logger.info(f"Successfully processed document #{doc.id} - Risk Score: {risk_eval['overall_risk_score']}")
        return True

    except Exception as e:
        logger.error(f"Error in contract analysis pipeline for document #{document_id}: {e}", exc_info=True)
        try:
            doc = Document.objects.get(id=document_id)
            doc.status = Document.Status.UPLOADED
            doc.save()
        except Exception:
            pass
        return False

from django.test import TestCase
from apps.analysis.services.clause_classifier import ClauseClassifierService
from apps.analysis.services.regex_service import RegexExtractionService
from apps.analysis.services.risk_engine import RiskDetectionEngine
from apps.analysis.models import Clause, RiskAnalysis, RiskClauseItem


class ContractAnalysisEngineTests(TestCase):
    def test_clause_classification(self):
        confidential_text = "Recipient agrees to hold in strict confidence all proprietary non-disclosure information."
        c_type, confidence = ClauseClassifierService.classify_text(confidential_text)
        self.assertEqual(c_type, Clause.ClauseType.CONFIDENTIALITY)

        liability_text = "Provider's total aggregate liability shall be limited to fees paid under this agreement."
        c_type, confidence = ClauseClassifierService.classify_text(liability_text)
        self.assertEqual(c_type, Clause.ClauseType.LIABILITY)

    def test_regex_metadata_extraction(self):
        contract_text = "This Agreement shall be governed by the laws of the State of Delaware. Courts of Delaware shall have exclusive jurisdiction."
        meta = RegexExtractionService.extract_metadata(contract_text)
        self.assertIn("Delaware", meta['governing_law'])
        self.assertIn("Delaware", meta['jurisdiction'])

    def test_risk_detection_engine(self):
        risky_text = "Provider liability shall not be limited for any consequential damages. Provider may terminate this agreement at any time without cause immediately."
        eval_res = RiskDetectionEngine.evaluate_contract(risky_text)
        self.assertGreaterEqual(eval_res['overall_risk_score'], 50)
        self.assertIn(eval_res['risk_level'], [RiskAnalysis.RiskLevel.HIGH, RiskAnalysis.RiskLevel.CRITICAL])
        self.assertGreater(len(eval_res['risk_items']), 0)

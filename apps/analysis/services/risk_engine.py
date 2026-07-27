import re
import logging
from apps.analysis.models import RiskAnalysis, RiskClauseItem

logger = logging.getLogger(__name__)


class RiskDetectionEngine:
    """
    Rule-based Legal Risk Detection Engine.
    Scans contract text and extracted clauses for high-risk legal terms,
    calculates risk score (0-100), assigns risk level, and generates
    actionable remediation recommendations.
    """

    RISK_RULES = [
        {
            'id': 'unlimited_liability',
            'title': 'Unlimited Liability Risk',
            'severity': RiskClauseItem.Severity.CRITICAL,
            'weight': 35,
            'pattern': r'\b(shall\s+not\s+be\s+limited|unlimited\s+liability|no\s+limitation\s+of\s+liability|without\s+limitation\s+for\s+any\s+damages)\b',
            'negation_pattern': r'\b(capped\s+at|limited\s+to\s+fees\s+paid|maximum\s+aggregate\s+liability)\b',
            'explanation': 'Contract contains terms suggesting unlimited financial liability or lacks a standard cap on aggregate damages.',
            'recommendation': 'Insert a standard limitation of liability clause capping aggregate liability to the fees paid under the contract in the preceding 12 months.'
        },
        {
            'id': 'unilateral_termination',
            'title': 'Unilateral Termination for Convenience',
            'severity': RiskClauseItem.Severity.HIGH,
            'weight': 25,
            'pattern': r'\b(terminate\s+(?:this\s+agreement\s+)?at\s+any\s+time\s+without\s+cause|terminate\s+immediately\s+upon\s+written\s+notice|terminate\s+for\s+convenience\s+without\s+penalty)\b',
            'explanation': 'Allows the counterparty to terminate the contract immediately or without cause, creating business operational instability.',
            'recommendation': 'Require mutual termination for convenience with at least a 30-day written notice period.'
        },
        {
            'id': 'broad_indemnification',
            'title': 'Broad Uncapped Indemnification',
            'severity': RiskClauseItem.Severity.HIGH,
            'weight': 25,
            'pattern': r'\b(indemnify,\s+defend\s+and\s+hold\s+harmless\s+from\s+and\s+against\s+any\s+and\s+all\s+claims|all\s+losses,\s+costs,\s+damages\s+and\s+expenses|including\s+reasonable\s+attorneys\s+fees)\b',
            'explanation': 'Overly broad indemnification obligation exposing company to indirect, third-party claims without financial caps.',
            'recommendation': 'Limit indemnification to direct third-party IP infringement claims and gross negligence/willful misconduct.'
        },
        {
            'id': 'perpetual_confidentiality',
            'title': 'Perpetual Confidentiality Obligation',
            'severity': RiskClauseItem.Severity.MEDIUM,
            'weight': 15,
            'pattern': r'\b(confidentiality\s+obligations\s+shall\s+survive\s+indefinitely|in\s+perpetuity|forever)\b',
            'explanation': 'Requires non-disclosure obligations to survive indefinitely, creating long-term compliance exposure.',
            'recommendation': 'Negotiate a standard confidentiality term of 3 to 5 years following termination, except for trade secrets.'
        },
        {
            'id': 'auto_renewal_trap',
            'title': 'Automatic Renewal without Notice',
            'severity': RiskClauseItem.Severity.MEDIUM,
            'weight': 15,
            'pattern': r'\b(automatically\s+renew|auto-renew|shall\s+renew\s+for\s+successive\s+terms)\b',
            'explanation': 'Contract automatically renews unless notice is given far in advance, risking unwanted multi-year lock-in.',
            'recommendation': 'Ensure non-renewal notice window is clear (e.g. 30 days before term end) and calendar reminder is scheduled.'
        },
        {
            'id': 'harsh_jurisdiction',
            'title': 'Foreign or Distant Jurisdiction',
            'severity': RiskClauseItem.Severity.LOW,
            'weight': 10,
            'pattern': r'\b(jurisdiction\s+of\s+the\s+courts\s+of\s+(?!Delaware|New\ York|California|England)[A-Z][a-z]+)\b',
            'explanation': 'Governing law or dispute venue is set in an inconvenient or unfamiliar court venue.',
            'recommendation': 'Request neutral or home state jurisdiction (e.g., Delaware, New York, or home state).'
        }
    ]

    @classmethod
    def evaluate_contract(cls, text, clauses=None):
        risk_items = []
        accumulated_score = 15  # Base baseline score

        for rule in cls.RISK_RULES:
            match = re.search(rule['pattern'], text, re.IGNORECASE)
            if match:
                # Check if negated
                if 'negation_pattern' in rule and re.search(rule['negation_pattern'], text, re.IGNORECASE):
                    continue

                snippet = cls._extract_snippet(text, match.start(), match.end())
                accumulated_score += rule['weight']

                risk_items.append({
                    'title': rule['title'],
                    'severity': rule['severity'],
                    'explanation': rule['explanation'],
                    'highlighted_text': snippet,
                    'recommendation': rule['recommendation']
                })

        overall_score = min(100, max(5, accumulated_score))

        if overall_score >= 70:
            level = RiskAnalysis.RiskLevel.CRITICAL if overall_score >= 85 else RiskAnalysis.RiskLevel.HIGH
        elif overall_score >= 40:
            level = RiskAnalysis.RiskLevel.MEDIUM
        else:
            level = RiskAnalysis.RiskLevel.LOW

        high_count = sum(1 for item in risk_items if item['severity'] in [RiskClauseItem.Severity.HIGH, RiskClauseItem.Severity.CRITICAL])
        med_count = sum(1 for item in risk_items if item['severity'] == RiskClauseItem.Severity.MEDIUM)
        low_count = sum(1 for item in risk_items if item['severity'] == RiskClauseItem.Severity.LOW)

        summary = f"Contract analyzed with overall risk score {overall_score}/100 ({level}). Detected {len(risk_items)} key risk issues ({high_count} High/Critical)."

        return {
            'overall_risk_score': overall_score,
            'risk_level': level,
            'risk_summary': summary,
            'high_risk_count': high_count,
            'medium_risk_count': med_count,
            'low_risk_count': low_count,
            'risk_items': risk_items
        }

    @staticmethod
    def _extract_snippet(text, start, end, padding=120):
        snippet_start = max(0, start - padding)
        snippet_end = min(len(text), end + padding)
        snippet = text[snippet_start:snippet_end].replace('\n', ' ').strip()
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(text):
            snippet = snippet + "..."
        return snippet

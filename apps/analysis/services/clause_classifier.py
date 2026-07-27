import re
import logging
from apps.analysis.models import Clause

logger = logging.getLogger(__name__)


class ClauseClassifierService:
    """
    Classifies legal contract text segments into 7 core clause types:
    1. Confidentiality
    2. Liability / Limitation of Liability
    3. Indemnification
    4. Termination
    5. Force Majeure
    6. Arbitration & Dispute Resolution
    7. Intellectual Property
    8. General
    """

    PATTERNS = {
        Clause.ClauseType.CONFIDENTIALITY: [
            r'\b(confidential|proprietary|trade\s+secret|non-disclosure|disclose|recipient|disclosing\s+party)\b',
        ],
        Clause.ClauseType.LIABILITY: [
            r'\b(limitation\s+of\s+liability|liable|consequential\s+damages|indirect\s+damages|punitive|aggregate\ |maximum\s+liability|cap\s+on\s+liability)\b',
        ],
        Clause.ClauseType.INDEMNIFICATION: [
            r'\b(indemnif|hold\s+harmless|defend|indemnitor|indemnitee|reimburse|losses|damages|claims)\b',
        ],
        Clause.ClauseType.TERMINATION: [
            r'\b(terminat|cancel|expire|notice\s+of\s+termination|material\s+breach|convenience|surviv)\b',
        ],
        Clause.ClauseType.FORCE_MAJEURE: [
            r'\b(force\s+majeure|act\s+of\s+god|war|epidemic|pandemic|natural\ disaster|unforeseeable|beyond\s+reasonable\s+control)\b',
        ],
        Clause.ClauseType.ARBITRATION: [
            r'\b(arbitrat|dispute\s+resolution|governing\s+law|jurisdiction|venue|court|litigat|mediation)\b',
        ],
        Clause.ClauseType.INTELLECTUAL_PROPERTY: [
            r'\b(intellectual\s+property|patent|copyright|trademark|work\s+made\s+for\s+hire|ownership|license|infringement)\b',
        ]
    }

    @classmethod
    def classify_text(cls, text):
        text_lower = text.lower()
        scores = {}

        for clause_type, patterns in cls.PATTERNS.items():
            count = 0
            for pat in patterns:
                matches = re.findall(pat, text_lower)
                count += len(matches)
            if count > 0:
                scores[clause_type] = count

        if not scores:
            return Clause.ClauseType.GENERAL, 0.5

        # Return category with highest pattern match count
        best_type = max(scores, key=scores.get)
        confidence = min(0.95, 0.6 + (scores[best_type] * 0.1))
        return best_type, round(confidence, 2)

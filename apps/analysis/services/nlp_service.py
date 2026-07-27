import spacy
import logging
import re

logger = logging.getLogger(__name__)

# Cache loaded spaCy model globally
_nlp = None

def get_spacy_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            logger.warning("spaCy model 'en_core_web_sm' not found. Installing or creating basic blank model.")
            try:
                from spacy.cli import download
                download("en_core_web_sm")
                _nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"Failed to auto-download spaCy model: {e}. Falling back to blank English model.")
                _nlp = spacy.blank("en")
    return _nlp


class NLPEngineService:
    """
    NLP Entity & Sentence Breakdown Engine using spaCy.
    Extracts Organizations (Companies), Dates, Locations, and Sentences.
    """

    @staticmethod
    def extract_entities(text):
        nlp = get_spacy_nlp()
        doc = nlp(text[:100000])  # Cap long text for performance

        companies = set()
        dates = set()
        locations = set()

        for ent in doc.ents:
            clean_text = ent.text.strip()
            if len(clean_text) < 2:
                continue

            if ent.label_ == "ORG":
                # Filter out obvious legal words
                if not re.search(r'\b(agreement|contract|section|article|exhibit|clause|terms|conditions)\b', clean_text, re.I):
                    companies.add(clean_text)
            elif ent.label_ in ("DATE", "TIME"):
                dates.add(clean_text)
            elif ent.label_ in ("GPE", "LOC"):
                locations.add(clean_text)

        return {
            'companies': sorted(list(companies)),
            'dates': sorted(list(dates)),
            'locations': sorted(list(locations)),
        }

    @staticmethod
    def extract_sentences(text):
        """Splits document text into clean structured sentences for clause classification."""
        nlp = get_spacy_nlp()
        if "sentencizer" not in nlp.pipe_names and "parser" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")

        doc = nlp(text[:200000])
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
        return sentences

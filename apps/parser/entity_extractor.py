import logging
from apps.parser.services import NLPService

logger = logging.getLogger(__name__)


class EntityExtractionService:
    """
    Service for performing Named Entity Recognition (NER) on text blocks using spaCy.
    Extracts organizations, dates, locations, and persons in a structured format.
    """

    def __init__(self, nlp_service: NLPService = None):
        self.nlp_service = nlp_service or NLPService()
        self.nlp = self.nlp_service.nlp

    def extract_entities(self, text: str) -> dict:
        """
        Analyzes the text and extracts named entities.
        Returns a dictionary with deduplicated and sorted lists:
        {
            "organizations": list[str],
            "dates": list[str],
            "locations": list[str],
            "persons": list[str]
        }
        """
        # Return empty structured schema if input is empty or invalid
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "organizations": [],
                "dates": [],
                "locations": [],
                "persons": []
            }

        logger.info("Initializing spaCy Named Entity Recognition (NER) processing.")
        
        # Use sets to automatically handle deduplication
        entities = {
            "organizations": set(),
            "dates": set(),
            "locations": set(),
            "persons": set()
        }

        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                ent_text = ent.text.strip()
                if not ent_text:
                    continue
                
                # Map spaCy entity labels to target keys
                # - ORG: Companies, agencies, institutions, etc.
                # - DATE: Absolute or relative dates or periods.
                # - GPE: Countries, cities, states.
                # - LOC: Non-GPE locations, mountain ranges, bodies of water.
                # - PERSON: People, including fictional.
                if ent.label_ == "ORG":
                    entities["organizations"].add(ent_text)
                elif ent.label_ == "DATE":
                    entities["dates"].add(ent_text)
                elif ent.label_ in ("GPE", "LOC"):
                    entities["locations"].add(ent_text)
                elif ent.label_ == "PERSON":
                    entities["persons"].add(ent_text)

            # Sort items to return stable, alphabetically ordered elements
            structured_entities = {
                "organizations": sorted(list(entities["organizations"])),
                "dates": sorted(list(entities["dates"])),
                "locations": sorted(list(entities["locations"])),
                "persons": sorted(list(entities["persons"]))
            }
            
            logger.info(
                f"Successfully completed NER extraction. Extracted: "
                f"{len(structured_entities['organizations'])} orgs, "
                f"{len(structured_entities['dates'])} dates, "
                f"{len(structured_entities['locations'])} locations, "
                f"{len(structured_entities['persons'])} persons."
            )
            return structured_entities

        except Exception as e:
            logger.error(f"Error during NER entity extraction: {str(e)}", exc_info=True)
            raise ValueError("Failed to extract entities from text due to an internal NLP error.") from e

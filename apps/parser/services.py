import logging
import spacy
from django.conf import settings

logger = logging.getLogger(__name__)


class NLPService:
    """
    Reusable Service for performing natural language processing operations using spaCy.
    """
    _nlp_model = None

    @classmethod
    def load_model(cls) -> spacy.language.Language:
        """
        Loads and caches the spaCy language model class-wide.
        To optimize loading time and memory footprint, unused pipeline components
        such as Named Entity Recognition ('ner') are disabled.
        """
        if cls._nlp_model is None:
            model_name = getattr(settings, 'SPACY_MODEL_NAME', 'en_core_web_sm')
            logger.info(f"Initializing spaCy model: '{model_name}'...")
            try:
                # Load the full model including the NER component
                cls._nlp_model = spacy.load(model_name)
                logger.info(f"Successfully loaded spaCy model: '{model_name}'")
            except Exception as e:
                logger.error(f"Failed to load spaCy model '{model_name}': {str(e)}", exc_info=True)
                raise RuntimeError(
                    f"Could not load spaCy model '{model_name}'. Ensure the model is downloaded and installed."
                ) from e
        return cls._nlp_model

    def __init__(self):
        # Load and retrieve the cached spaCy model instance
        self.nlp = self.load_model()

    def preprocess_text(self, text: str, remove_stopwords: bool = True, lowercase: bool = True) -> str:
        """
        Preprocesses raw text:
        - Removes punctuation and extra spaces.
        - Optionally removes stop words.
        - Normalizes tokens to their root lemma.
        - Optionally converts result to lowercase.
        """
        if not text or not isinstance(text, str):
            return ""

        try:
            doc = self.nlp(text)
            processed_tokens = []
            
            for token in doc:
                # Filter out punctuation and whitespace tokens
                if token.is_punct or token.is_space:
                    continue
                
                # Filter out stop words if requested
                if remove_stopwords and token.is_stop:
                    continue
                
                # Extract lemma (root form of the word)
                token_text = token.lemma_
                if lowercase:
                    token_text = token_text.lower()
                
                processed_tokens.append(token_text)
                
            return " ".join(processed_tokens)
        except Exception as e:
            logger.error(f"Error during NLP text preprocessing: {str(e)}", exc_info=True)
            raise ValueError("Failed to preprocess text due to an internal NLP error.") from e

    def tokenize_text(self, text: str) -> list[str]:
        """
        Tokenizes the input text into a list of word strings.
        """
        if not text or not isinstance(text, str):
            return []

        try:
            doc = self.nlp(text)
            return [token.text for token in doc if not token.is_space]
        except Exception as e:
            logger.error(f"Error during NLP text tokenization: {str(e)}", exc_info=True)
            raise ValueError("Failed to tokenize text due to an internal NLP error.") from e

    def sentence_segmentation(self, text: str) -> list[str]:
        """
        Segments the input text block into a list of individual sentence strings.
        """
        if not text or not isinstance(text, str):
            return []

        try:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        except Exception as e:
            logger.error(f"Error during NLP sentence segmentation: {str(e)}", exc_info=True)
            raise ValueError("Failed to segment sentences due to an internal NLP error.") from e

from django.test import SimpleTestCase
from django.test import override_settings
from apps.parser.services import NLPService
from apps.parser.entity_extractor import EntityExtractionService
import spacy


class NLPServiceTestCase(SimpleTestCase):
    def setUp(self):
        # Instantiate the NLPService (loads and caches model)
        self.nlp_service = NLPService()

    def test_model_caching(self):
        """
        Verify that the spaCy model is loaded and cached class-wide,
        returning the exact same object reference on subsequent requests.
        """
        model_instance_1 = NLPService.load_model()
        model_instance_2 = NLPService.load_model()
        
        self.assertIsNotNone(model_instance_1)
        self.assertIs(model_instance_1, model_instance_2)
        self.assertIsInstance(model_instance_1, spacy.language.Language)

    def test_preprocess_text(self):
        """
        Verify text preprocessing: lemmatization, stop words removal,
        lowercase conversion, and punctuation removal.
        """
        raw_text = "The quick brown foxes are jumping over the lazy dogs!"
        
        # Default behavior: remove stop words, convert to lowercase
        processed = self.nlp_service.preprocess_text(raw_text)
        
        # Expected lemmas:
        # "quick" -> "quick"
        # "brown" -> "brown"
        # "foxes" -> "fox"
        # "jumping" -> "jump"
        # "lazy" -> "lazy"
        # "dogs" -> "dog"
        # Stop words ("the", "are", "over") and punctuation ("!") are filtered out.
        self.assertNotIn("the", processed.split())
        self.assertNotIn("are", processed.split())
        self.assertIn("fox", processed.split())
        self.assertIn("jump", processed.split())
        self.assertIn("dog", processed.split())
        
        # Behavior without stop words filtering
        processed_with_stopwords = self.nlp_service.preprocess_text(raw_text, remove_stopwords=False)
        self.assertIn("the", processed_with_stopwords.split())
        self.assertIn("lazy", processed_with_stopwords.split())

    def test_tokenize_text(self):
        """
        Verify text is tokenized into word lists, filtering out spaces.
        """
        raw_text = "This is a simple contract."
        tokens = self.nlp_service.tokenize_text(raw_text)
        
        expected_tokens = ["This", "is", "a", "simple", "contract", "."]
        self.assertEqual(tokens, expected_tokens)

    def test_sentence_segmentation(self):
        """
        Verify text is split into distinct sentences.
        """
        raw_text = "First sentence. Second sentence! Third one?"
        sentences = self.nlp_service.sentence_segmentation(raw_text)
        
        expected_sentences = ["First sentence.", "Second sentence!", "Third one?"]
        self.assertEqual(sentences, expected_sentences)

    def test_empty_and_none_handling(self):
        """
        Verify that None, empty string, and non-string inputs do not crash the service,
        but return empty strings or lists.
        """
        # None inputs
        self.assertEqual(self.nlp_service.preprocess_text(None), "")
        self.assertEqual(self.nlp_service.tokenize_text(None), [])
        self.assertEqual(self.nlp_service.sentence_segmentation(None), [])
        
        # Empty string inputs
        self.assertEqual(self.nlp_service.preprocess_text(""), "")
        self.assertEqual(self.nlp_service.tokenize_text(""), [])
        self.assertEqual(self.nlp_service.sentence_segmentation(""), [])
        
        # Whitespace-only inputs
        self.assertEqual(self.nlp_service.preprocess_text("   "), "")
        self.assertEqual(self.nlp_service.tokenize_text("   "), [])
        self.assertEqual(self.nlp_service.sentence_segmentation("   "), [])

        # Non-string inputs
        self.assertEqual(self.nlp_service.preprocess_text(123), "")
        self.assertEqual(self.nlp_service.tokenize_text([]), [])
        self.assertEqual(self.nlp_service.sentence_segmentation({}), [])


class EntityExtractionTestCase(SimpleTestCase):
    def setUp(self):
        # Initialize EntityExtractionService
        self.extractor_service = EntityExtractionService()

    def test_extract_entities_success(self):
        """
        Verify that common named entities (Google, John Doe, New York, January 1, 2026)
        are correctly detected and mapped.
        """
        text = "On January 1, 2026, John Doe signed an agreement with Google in New York."
        entities = self.extractor_service.extract_entities(text)
        
        # Verify JSON schema keys
        self.assertIn("organizations", entities)
        self.assertIn("dates", entities)
        self.assertIn("locations", entities)
        self.assertIn("persons", entities)
        
        # Verify extracted content values
        self.assertIn("Google", entities["organizations"])
        self.assertIn("January 1, 2026", entities["dates"])
        self.assertIn("New York", entities["locations"])
        self.assertIn("John Doe", entities["persons"])

    def test_extract_entities_deduplication(self):
        """
        Verify that duplicate entities are merged and only appear once in lists.
        """
        text = "John Doe works at Google. John Doe likes Google."
        entities = self.extractor_service.extract_entities(text)
        
        self.assertEqual(entities["organizations"].count("Google"), 1)
        self.assertEqual(entities["persons"].count("John Doe"), 1)

    def test_extract_entities_empty(self):
        """
        Verify that empty, None, whitespace, and non-string inputs return the standard empty dictionary template.
        """
        empty_schema = {
            "organizations": [],
            "dates": [],
            "locations": [],
            "persons": []
        }
        self.assertEqual(self.extractor_service.extract_entities(""), empty_schema)
        self.assertEqual(self.extractor_service.extract_entities(None), empty_schema)
        self.assertEqual(self.extractor_service.extract_entities("   "), empty_schema)
        self.assertEqual(self.extractor_service.extract_entities(12345), empty_schema)
        self.assertEqual(self.extractor_service.extract_entities([]), empty_schema)

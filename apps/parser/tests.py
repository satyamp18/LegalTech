from django.test import SimpleTestCase
from django.test import override_settings
from apps.parser.services import NLPService
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
        Verify that None and empty string inputs do not crash the service,
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

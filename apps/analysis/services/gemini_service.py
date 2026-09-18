import os
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


class GeminiService:
    """
    Service wrapper for Google Gemini API integration.
    Provides simple contract summarization, clause explanation, and AI risk analysis.
    Uses environment variables for API key and includes error handling/fallbacks.
    """

    @classmethod
    def get_api_key(cls) -> str:
        """Returns the configured Gemini API key or empty string."""
        return os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()

    @classmethod
    def is_available(cls) -> bool:
        """Checks if a Gemini API key is configured."""
        return bool(cls.get_api_key())

    @classmethod
    def _call_gemini_api(cls, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Private helper to send prompt to Gemini REST API.
        Handles timeout, network errors, and invalid API responses gracefully.
        """
        api_key = cls.get_api_key()
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is missing.")
            return None

        url = f"{GEMINI_API_URL}?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2
            }
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=12)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                logger.warning(f"Unexpected response structure from Gemini API: {data}")
                return None
            else:
                logger.error(f"Gemini API returned status code {response.status_code}: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out after 12 seconds.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API network failure: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini API: {e}", exc_info=True)
            return None

    @classmethod
    def summarize_contract(cls, text: str) -> str:
        """
        Generates a concise 3-4 sentence executive summary of the contract text.
        """
        if not text or len(text.strip()) == 0:
            return "No text available to summarize."

        if not cls.is_available():
            return "AI Summary unavailable: GEMINI_API_KEY is not configured in environment variables."

        sample_text = text[:8000]  # Cap length for prompt payload
        prompt = (
            "You are a professional legal contract assistant. Provide a clear, concise, "
            "3 to 4 sentence executive summary of the following legal contract. Highlight the agreement type, "
            "key parties, primary obligation, and termination/duration if present:\n\n"
            f"{sample_text}"
        )

        summary = cls._call_gemini_api(prompt, max_tokens=350)
        if summary:
            return summary
        return "AI Executive Summary is temporarily unavailable. (Check API key or network connection)."

    @classmethod
    def explain_clause(cls, clause_text: str, clause_type: str = "GENERAL") -> str:
        """
        Translates a legal clause into plain, easy-to-understand language.
        """
        if not clause_text or len(clause_text.strip()) == 0:
            return "Empty clause text provided."

        if not cls.is_available():
            return "Clause explanation unavailable: GEMINI_API_KEY is not configured."

        prompt = (
            f"You are a legal assistant. Explain this legal clause (Category: {clause_type}) "
            "in simple, non-legal terms so a non-lawyer can easily understand what it means and why it matters:\n\n"
            f"\"{clause_text}\""
        )

        explanation = cls._call_gemini_api(prompt, max_tokens=250)
        if explanation:
            return explanation
        return "Plain-language explanation temporarily unavailable."

    @classmethod
    def analyze_contract_risks(cls, text: str) -> str:
        """
        Asks Gemini for strategic risk insights and negotiation advice for the contract.
        """
        if not text or len(text.strip()) == 0:
            return "No text provided for risk analysis."

        if not cls.is_available():
            return "AI Risk Insights unavailable: GEMINI_API_KEY not configured."

        sample_text = text[:8000]
        prompt = (
            "Analyze the following legal contract snippet for potential business or legal risks. "
            "Provide 3 bullet points listing top potential risk areas and 1 actionable negotiation tip:\n\n"
            f"{sample_text}"
        )

        ai_risks = cls._call_gemini_api(prompt, max_tokens=400)
        if ai_risks:
            return ai_risks
        return "AI Risk Analysis temporarily unavailable."

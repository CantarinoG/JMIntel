import time
from google import genai
from typing import Any, Dict, Optional
from src.ai_services.base_ai_service import BaseAIService

class GeminiService(BaseAIService):
    """
    Concrete implementation of BaseAIService using the modern google-genai SDK.
    """

    def __init__(self):
        super().__init__()
        self._client = None
        self._model_name = "gemini-3.1-flash-lite-preview"

    def configure(self, api_key: str, settings: Optional[Dict[str, Any]] = None):
        """
        Configure the Gemini Client with the Provided API Key.
        """
        self._client = genai.Client(api_key=api_key)

        if settings and "model_name" in settings:
            self._model_name = settings["model_name"]

    def process(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the response text.
        Handles 429 Rate Limit errors by waiting 60 seconds and retrying.
        """
        if not self._client:
            raise ValueError(
                "GeminiService is not configured. Call configure() first with your API key."
            )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                error_msg = str(e)
                print(error_msg)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    time.sleep(60)
                    continue

                return f"Error communicating with Gemini: {error_msg}"

        return "Failed to get response after multiple retries due to rate limits."
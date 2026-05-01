from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAIService(ABC):
    """
    Abstract base class for all AI service providers (Gemini, OpenAI, etc.).
    Ensures that the application can switch between LLM models with minimal impact.
    """

    @abstractmethod
    def configure(self, api_key: str, settings: Optional[Dict[str, Any]] = None):
        """
        Configure the AI service with an API key and optional settings.
        """
        pass

    @abstractmethod
    def process(self, prompt: str) -> str:
        """
        Process a prompt through the LLM.
        Returns the LLM's response as a string.
        """
        pass
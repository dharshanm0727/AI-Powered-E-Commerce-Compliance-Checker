from app.core.config import settings
from app.services.ai.base import BaseAIService
from app.services.ai.providers.mock_provider import MockAIProvider
from app.services.ai.providers.gemini_provider import GeminiAIProvider
from app.services.ai.providers.openai_provider import OpenAIProvider

def get_ai_service() -> BaseAIService:
    provider = (settings.LLM_PROVIDER or "mock").lower()
    if provider == "gemini":
        return GeminiAIProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        return MockAIProvider()

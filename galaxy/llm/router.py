from typing import List, Dict, AsyncGenerator
from .base import LLMBase
from .local import LocalOllama
from .api import GroqLLM, GeminiLLM, MistralAPILLM
from galaxy.config.settings import settings

class LLMRouter:
    def __init__(self):
        self.local = LocalOllama()
        self.groq = GroqLLM()
        self.gemini = GeminiLLM()
        self.mistral_api = MistralAPILLM()
        
    async def get_best_model(self, complexity: str = "simple") -> LLMBase:
        # Check provider preferences first
        pref = settings.PREFERRED_PROVIDER.lower()
        if pref == "local" and await self.local.is_healthy():
            return self.local
        elif pref == "mistral":
            if await self.local.is_healthy():
                return self.local
            if await self.mistral_api.is_healthy():
                return self.mistral_api
            if await self.groq.is_healthy():
                return self.groq
        elif pref == "gemini" and await self.gemini.is_healthy():
            return self.gemini
        elif pref == "groq" and await self.groq.is_healthy():
            return self.groq

        # Auto fallback logic:
        # 1. If local Ollama is running, prefer local for privacy & unlimited tokens
        if await self.local.is_healthy():
            return self.local

        # 2. Free API fallbacks
        if await self.gemini.is_healthy():
            return self.gemini
        if await self.groq.is_healthy():
            return self.groq
        if await self.mistral_api.is_healthy():
            return self.mistral_api

        # 3. Final check: if local host is set, try local anyway
        return self.local

    async def generate(self, messages: List[Dict[str, str]], complexity: str = "simple", **kwargs) -> str:
        model = await self.get_best_model(complexity)
        return await model.generate(messages, **kwargs)
        
    async def stream(self, messages: List[Dict[str, str]], complexity: str = "simple", **kwargs) -> AsyncGenerator[str, None]:
        model = await self.get_best_model(complexity)
        async for chunk in model.stream(messages, **kwargs):
            yield chunk

llm_router = LLMRouter()

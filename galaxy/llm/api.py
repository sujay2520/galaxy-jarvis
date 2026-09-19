import httpx
from typing import List, Dict, AsyncGenerator
from .base import LLMBase
from galaxy.config.settings import settings

class GroqLLM(LLMBase):
    def __init__(self, model: str = None):
        self.model = model or (settings.GROQ_MISTRAL_MODEL if "mistral" in settings.PREFERRED_MODEL.lower() else settings.GROQ_MODEL)
        
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        import json
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                }
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk_str = line[6:]
                        try:
                            chunk_data = json.loads(chunk_str)
                            delta = chunk_data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except Exception:
                            continue
                
    async def is_healthy(self) -> bool:
        return bool(settings.GROQ_API_KEY and len(settings.GROQ_API_KEY.strip()) > 5)


class MistralAPILLM(LLMBase):
    """Direct Mistral AI cloud API client (https://api.mistral.ai)."""
    def __init__(self, model: str = None):
        self.model = model or settings.MISTRAL_API_MODEL

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        import json
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                }
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk_str = line[6:]
                        try:
                            chunk_data = json.loads(chunk_str)
                            delta = chunk_data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except Exception:
                            continue

    async def is_healthy(self) -> bool:
        return bool(settings.MISTRAL_API_KEY and len(settings.MISTRAL_API_KEY.strip()) > 5)


class GeminiLLM(LLMBase):
    def __init__(self, model: str = None):
        self.model = model or settings.GEMINI_MODEL
        
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        resp = client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return resp.text
        
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        resp = client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
        )
        for chunk in resp:
            yield chunk.text
            
    async def is_healthy(self) -> bool:
        return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5)

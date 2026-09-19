import httpx
from typing import List, Dict, AsyncGenerator, Optional
from .base import LLMBase
from galaxy.config.settings import settings
import json

class LocalOllama(LLMBase):
    def __init__(self, model: Optional[str] = None):
        self.host = settings.OLLAMA_HOST
        # Default to preferred local model (mistral if set, else qwen2.5:3b)
        self.model = model or (settings.MISTRAL_LOCAL_MODEL if settings.PREFERRED_MODEL.startswith("mistral") else settings.DEFAULT_LOCAL_MODEL)
        
    async def list_models(self) -> List[str]:
        """Fetch all currently downloaded models in Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.host}/api/tags", timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def get_active_model(self) -> str:
        """Check available models and pick best installed model (preferring Mistral)."""
        installed = await self.list_models()
        if not installed:
            return self.model
        
        # Look for Mistral first if user prefers it
        for m in installed:
            if "mistral" in m.lower():
                return m
        for m in installed:
            if "qwen" in m.lower():
                return m
        return installed[0]

    async def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        target_model = model or self.model
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.host}/api/chat",
                json={
                    "model": target_model,
                    "messages": messages,
                    "stream": False
                },
                timeout=180.0
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
            
    async def stream(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        target_model = model or self.model
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                f"{self.host}/api/chat",
                json={
                    "model": target_model,
                    "messages": messages,
                    "stream": True
                },
                timeout=180.0
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_lines():
                    if chunk:
                        data = json.loads(chunk)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        
    async def is_healthy(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.host}/api/tags", timeout=3.0)
                return resp.status_code == 200
        except Exception:
            return False

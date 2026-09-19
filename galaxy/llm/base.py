from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Any

class LLMBase(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass
        
    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        pass
        
    @abstractmethod
    async def is_healthy(self) -> bool:
        pass

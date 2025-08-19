from abc import ABC, abstractmethod
from typing import AsyncIterator, Any


class AgentAdapter(ABC):
    @abstractmethod
    async def generate_response(self, session_id: str, content: str) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, session_id: str, content: str) -> AsyncIterator[Any]:
        pass

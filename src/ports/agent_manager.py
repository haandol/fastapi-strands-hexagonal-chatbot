from abc import ABC, abstractmethod


class AgentManager(ABC):
    @abstractmethod
    async def generate_response(self, content: str) -> str:
        pass

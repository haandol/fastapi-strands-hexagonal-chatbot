from abc import ABC, abstractmethod
from typing import Dict, Any


class SessionAdapter(ABC):
    @abstractmethod
    async def create_session(self, user_id: str) -> str:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def delete_session(self, user_id: str) -> None:
        pass

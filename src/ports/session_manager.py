from typing import Dict, Any
from abc import ABC, abstractmethod


class SessionManager(ABC):
    @abstractmethod
    async def create_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        pass

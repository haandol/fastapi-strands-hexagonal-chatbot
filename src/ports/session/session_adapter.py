from abc import ABC, abstractmethod

from strands.session.repository_session_manager import RepositorySessionManager


class SessionAdapter(ABC):
    @abstractmethod
    async def create_session(self, user_id: str) -> str:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> RepositorySessionManager:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        pass

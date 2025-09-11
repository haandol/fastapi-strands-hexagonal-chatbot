from abc import ABC, abstractmethod

from strands.session.repository_session_manager import RepositorySessionManager


class SessionAdapter(ABC):
    @abstractmethod
    async def create_session(self, user_id: str) -> str:
        """Create session for user"""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete session by session_id"""
        pass

    @abstractmethod
    def get_session_user(self, session_id: str) -> str:
        """Get user id of the session"""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> RepositorySessionManager:
        """Get RepositorySessionManager by session_id"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

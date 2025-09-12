from abc import ABC, abstractmethod
from typing import List

from strands.types.session import SessionMessage
from strands.session.repository_session_manager import RepositorySessionManager


class SessionAdapter(ABC):
    @abstractmethod
    async def create_session(self, user_id: str) -> str:
        """Create session for user"""
        pass

    @abstractmethod
    async def get_session(self, user_id: str, session_id: str) -> RepositorySessionManager:
        """Get RepositorySessionManager by session_id"""
        pass

    @abstractmethod
    async def get_user_session_ids(self, user_id: str) -> List[str]:
        """Get all sessions for user"""
        pass

    @abstractmethod
    async def delete_session(self, user_id: str, session_id: str) -> None:
        """Delete session by session_id"""
        pass

    @abstractmethod
    async def list_messages(self, user_id: str, session_id: str) -> List[SessionMessage]:
        """List messages of the session"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

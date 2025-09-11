from typing import Dict, override

import ulid
from strands.session.file_session_manager import FileSessionManager

from ports.adapters.secondary import SessionAdapter
from utils.logger import logger


class StrandsFileSessionAdapter(SessionAdapter):
    def __init__(self, base_path: str = "./.sessions"):
        self.base_path = base_path
        self._session_user: Dict[str, str] = {}
        self._sessions: Dict[str, FileSessionManager] = {}

    @property
    def sessions(self) -> Dict[str, FileSessionManager]:
        return self._sessions

    @override
    async def create_session(self, user_id: str) -> str:
        session_id = ulid.ulid()
        self.sessions[session_id] = FileSessionManager(
            session_id=session_id,
            storage_dir=self.base_path,
        )
        self._session_user[session_id] = user_id
        logger.info("session created", session_id=session_id, user_id=user_id)
        return session_id

    @override
    def get_session_user(self, session_id: str) -> str:
        if session_id not in self._session_user:
            logger.error(
                "🚨 session not found",
                session_id=session_id,
                exc_info=True,
                stack_info=True,
            )
            raise KeyError(f"🚨 session user not found: {session_id}")

        return self._session_user[session_id]

    @override
    def get_session(self, session_id: str) -> FileSessionManager:
        if session_id not in self.sessions:
            logger.error(
                "🚨 session not found",
                session_id=session_id,
                exc_info=True,
                stack_info=True,
            )
            raise KeyError(f"🚨 session not found: {session_id}")
        return self.sessions[session_id]

    @override
    def delete_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            logger.warn("session not found", session_id=session_id)
            return

        del self.sessions[session_id]
        logger.info("session deleted", session_id=session_id)

    @override
    async def cleanup(self) -> None:
        logger.info("🧹 cleaning up session adapter")

        self.sessions.clear()

        logger.info("🧹 session adapter cleaned up")

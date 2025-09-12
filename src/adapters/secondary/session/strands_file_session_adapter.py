from pathlib import Path
from typing import Dict, override, List

import ulid
from strands.types.session import SessionMessage
from strands.session.file_session_manager import FileSessionManager

from ports.adapters.secondary import SessionAdapter
from utils.logger import logger


class StrandsFileSessionAdapter(SessionAdapter):
    def __init__(self, base_path: str = "./.sessions"):
        self.base_path = base_path
        self._sessions: Dict[str, FileSessionManager] = {}

    @property
    def sessions(self) -> Dict[str, FileSessionManager]:
        return self._sessions

    @override
    async def create_session(self, user_id: str) -> str:
        session_id = ulid.ulid()
        # Create user-specific directory structure
        user_dir = Path(self.base_path) / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        self.sessions[session_id] = FileSessionManager(
            session_id=session_id,
            storage_dir=str(user_dir),
        )
        logger.info("file session created", session_id=session_id, user_id=user_id)
        return session_id

    @override
    async def get_user_session_ids(self, user_id: str) -> List[str]:
        user_dir = Path(self.base_path) / f"user_{user_id}"
        if not user_dir.exists():
            return []

        return [dir.name.split("_")[1] for dir in user_dir.glob("session_*") if dir.is_dir()]

    @override
    async def get_session(self, user_id: str, session_id: str) -> FileSessionManager:
        if session_id not in self.sessions:
            logger.info("file session not found, restore old session", session_id=session_id)
            try:
                session_dir = Path(self.base_path) / f"user_{user_id}"
                if not session_dir.exists():
                    raise ValueError(f"Session {session_id} not found in user directory")

                self.sessions[session_id] = FileSessionManager(
                    session_id=session_id,
                    storage_dir=str(session_dir),
                )
            except Exception:
                logger.error(
                    "error restoring old session",
                    session_id=session_id,
                    exc_info=True,
                    stack_info=True,
                )
                raise

        return self.sessions[session_id]

    @override
    async def list_messages(self, user_id: str, session_id: str) -> List[SessionMessage]:
        session_manager = await self.get_session(user_id, session_id)
        try:
            return session_manager.list_messages(
                session_id=session_id,
                agent_id="default",
            )
        except Exception:
            logger.error(
                "error listing messages",
                session_id=session_id,
                exc_info=True,
                stack_info=True,
            )
            return []

    @override
    async def delete_session(self, user_id: str, session_id: str) -> None:
        if session_id not in self.sessions:
            logger.warn("file session not found", session_id=session_id)
            return

        del self.sessions[session_id]
        logger.info("file session deleted", session_id=session_id)

    @override
    async def cleanup(self) -> None:
        logger.info("🧹 cleaning up file session adapter")

        self.sessions.clear()

        logger.info("🧹 file session adapter cleaned up")

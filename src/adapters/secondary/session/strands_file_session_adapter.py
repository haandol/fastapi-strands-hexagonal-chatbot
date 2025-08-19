from typing import Dict

import ulid
from strands.session.file_session_manager import FileSessionManager

from ports.session.session_adapter import SessionAdapter
from utils.logger import logger


class StrandsFileSessionAdapter(SessionAdapter):
    def __init__(self, base_path: str = "./.sessions"):
        self.base_path = base_path
        self.sessions: Dict[str, FileSessionManager] = {}

    # TODO: get involved with user_id
    async def create_session(self, user_id: str) -> str:
        session_id = ulid.ulid()
        self.sessions[session_id] = FileSessionManager(
            session_id=session_id,
            storage_dir=self.base_path,
        )
        return session_id

    async def get_session(self, session_id: str) -> FileSessionManager:
        if session_id not in self.sessions:
            logger.error("🚨 session not found", session_id=session_id, exc_info=True, stack_info=True)
            raise KeyError(f"🚨 session not found: {session_id}")
        return self.sessions[session_id]

    async def delete_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            return

        del self.sessions[session_id]

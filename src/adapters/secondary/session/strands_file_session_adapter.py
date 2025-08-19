from typing import Dict, Set

import ulid
from strands.session.file_session_manager import FileSessionManager

from ports.session.session_adapter import SessionAdapter
from utils.logger import logger


class StrandsFileSessionAdapter(SessionAdapter):
    def __init__(self, base_path: str = "./.sessions"):
        self.base_path = base_path
        self.sessions: Dict[str, FileSessionManager] = {}
        self.session_ids: Set[str] = set()

    async def create_session(self, user_id: str) -> str:
        session_id = ulid.ulid()
        self.sessions[user_id] = FileSessionManager(
            session_id=session_id,
            storage_dir=self.base_path,
        )
        self.session_ids.add(session_id)
        return session_id

    async def get_session(self, session_id: str) -> str:
        if session_id in self.session_ids:
            return session_id
        logger.error("🚨 session not found", session_id=session_id)
        raise KeyError(f"🚨 session not found: {session_id}")

    async def delete_session(self, user_id: str) -> None:
        if user_id not in self.sessions:
            return

        self.session_ids.remove(user_id)
        del self.sessions[user_id]

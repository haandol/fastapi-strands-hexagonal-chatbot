from typing import Dict, Any

from ports.session_manager import SessionManager


class SessionService:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def create_session(self, user_id: str) -> str:
        return await self.session_manager.create_session(user_id)

    async def get_session(self, user_id: str) -> Dict[str, Any]:
        return await self.session_manager.get_session(user_id)

    async def delete_session(self, user_id: str) -> None:
        await self.session_manager.delete_session(user_id)

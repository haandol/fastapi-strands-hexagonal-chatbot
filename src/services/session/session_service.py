from typing import List

from strands.types.session import SessionMessage
from strands.session.repository_session_manager import RepositorySessionManager

from ports.adapters.secondary import SessionAdapter


class SessionService:
    def __init__(self, session_adapter: SessionAdapter):
        self.session_adapter = session_adapter

    async def create_session(self, user_id: str) -> str:
        return await self.session_adapter.create_session(user_id)

    async def get_session(self, user_id: str, session_id: str) -> RepositorySessionManager:
        return await self.session_adapter.get_session(user_id, session_id)

    async def get_user_session_ids(self, user_id: str) -> List[str]:
        return await self.session_adapter.get_user_session_ids(user_id)

    async def list_messages(self, user_id: str, session_id: str) -> List[SessionMessage]:
        return await self.session_adapter.list_messages(user_id, session_id)

    async def delete_session(self, user_id: str, session_id: str) -> None:
        await self.session_adapter.delete_session(user_id, session_id)

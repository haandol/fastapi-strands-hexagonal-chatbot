from strands.session.repository_session_manager import RepositorySessionManager

from ports.session import SessionAdapter


class SessionService:
    def __init__(self, session_adapter: SessionAdapter):
        self.session_adapter = session_adapter

    async def create_session(self, user_id: str) -> str:
        return await self.session_adapter.create_session(user_id)

    async def get_session(self, session_id: str) -> RepositorySessionManager:
        return await self.session_adapter.get_session(session_id)

    async def delete_session(self, session_id: str) -> None:
        await self.session_adapter.delete_session(session_id)

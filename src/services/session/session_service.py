from strands.session.repository_session_manager import RepositorySessionManager

from ports.adapters.secondary import SessionAdapter


class SessionService:
    def __init__(self, session_adapter: SessionAdapter):
        self.session_adapter = session_adapter

    async def create_session(self, user_id: str) -> str:
        return await self.session_adapter.create_session(user_id)

    def get_session(self, session_id: str) -> RepositorySessionManager:
        return self.session_adapter.get_session(session_id)

    def delete_session(self, session_id: str) -> None:
        self.session_adapter.delete_session(session_id)

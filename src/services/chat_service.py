from src.ports.agent_manager import AgentManager
from src.ports.session_manager import SessionManager


class ChatService:
    def __init__(
        self,
        agent_manager: AgentManager,
        session_manager: SessionManager,
    ):
        self.agent_manager = agent_manager
        self.session_manager = session_manager

    async def process_message(self, content: str, session_id: str) -> str:
        # Ensure session exists
        try:
            await self.session_manager.get_session_data(session_id)
        except Exception:
            await self.session_manager.create_session(session_id)

        return await self.agent_manager.generate_response(content)

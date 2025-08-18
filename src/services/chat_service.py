from typing import AsyncGenerator, Union

from ports.agent_manager import AgentManager
from ports.session_manager import SessionManager


class ChatService:
    def __init__(
        self,
        agent_manager: AgentManager,
        session_manager: SessionManager,
    ):
        self.agent_manager = agent_manager
        self.session_manager = session_manager

    async def invoke_async(self, session_id: str, content: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        # Ensure session exists
        try:
            await self.session_manager.get_session_data(session_id)
        except Exception:
            await self.session_manager.create_session(session_id)

        if stream:
            return await self.agent_manager.generate_response_stream(session_id, content)
        else:
            return await self.agent_manager.generate_response(session_id, content)

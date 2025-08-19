from typing import AsyncIterator, Any, Union

from ports.chat import AgentAdapter
from ports.session import SessionAdapter


class ChatService:
    def __init__(
        self,
        agent_adapter: AgentAdapter,
        session_adapter: SessionAdapter,
    ):
        self.agent_adapter = agent_adapter
        self.session_adapter = session_adapter

    async def generate_response(self, session_id: str, content: str, stream: bool = False) -> Union[str, AsyncIterator[Any]]:
        # Ensure session exists
        try:
            await self.session_adapter.get_session(session_id)
        except Exception:
            await self.session_adapter.create_session(session_id)

        if stream:
            return await self.agent_adapter.generate_response_stream(session_id, content)
        else:
            return await self.agent_adapter.generate_response(session_id, content)

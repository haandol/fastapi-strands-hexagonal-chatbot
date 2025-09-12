import pytest
from typing import AsyncIterator, Any, Optional, List, Dict

from services.chat.chat_service import ChatService
from ports.adapters.secondary.mcp_agent_adapter import MCPAgentAdapter
from ports.adapters.secondary.session_adapter import SessionAdapter
from strands import Agent
from strands.session.repository_session_manager import RepositorySessionManager
from ports.interfaces.mcp import MCPConfig


class DummyAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id


class DummyAgentAdapter(MCPAgentAdapter):
    async def generate_response(self, agent: Agent, content: str) -> str:
        return f"echo: {content}"

    async def generate_stream_response(self, agent: Agent, content: str) -> AsyncIterator[Any]:
        async def iterator():
            yield {"data": "first"}
            yield {"data": "second"}
        return iterator()

    async def generate_messages(self, agent: Agent, content: str) -> List[Dict[str, Any]]:
        return [{"role": "user", "content": content}]

    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        pass

    def get_user_preferences(self, user_id: str) -> Optional[str]:
        return None

    def create_agent(
        self,
        user_id: str,
        system_prompt: Optional[str] = None,
        session_manager: Optional[RepositorySessionManager] = None,
    ) -> Agent:
        return DummyAgent(user_id)

    async def cleanup(self) -> None:
        pass


class DummySessionAdapter(SessionAdapter):
    async def create_session(self, user_id: str) -> str:
        return "session"

    async def get_session(self, user_id: str, session_id: str):
        class DummySession:
            def __init__(self, session_id: str):
                self.session_id = session_id
        return DummySession(session_id)

    async def get_user_session_ids(self, user_id: str) -> List[str]:
        return ["session"]

    async def list_messages(self, user_id: str, session_id: str) -> List[Any]:
        return []

    async def delete_session(self, user_id: str, session_id: str) -> None:
        pass

    async def cleanup(self) -> None:
        pass


@pytest.mark.asyncio
async def test_generate_response_non_stream():
    service = ChatService(DummyAgentAdapter(), DummySessionAdapter())
    result = await service.generate_response("user1", "session", "hello", stream=False)
    assert result == "echo: hello"


@pytest.mark.asyncio
async def test_generate_response_stream():
    service = ChatService(DummyAgentAdapter(), DummySessionAdapter())
    stream = await service.generate_response("user1", "session", "hello", stream=True)
    chunks = [chunk async for chunk in stream]
    assert chunks == [{"data": "first"}, {"data": "second"}]

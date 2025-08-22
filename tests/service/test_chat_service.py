import pytest
from typing import AsyncIterator, Any

from services.chat.chat_service import ChatService
from ports.chat.mcp_agent_adapter import MCPAgentAdapter
from ports.session.session_adapter import SessionAdapter


class DummyAgentAdapter(MCPAgentAdapter):
    async def generate_response(self, session_manager, content: str) -> str:
        return f"echo: {content}"

    async def generate_response_stream(self, session_manager, content: str) -> AsyncIterator[Any]:
        async def iterator():
            yield {"data": "first"}
            yield {"data": "second"}
        return iterator()

    def configure_mcp(self, mcp_config=None) -> None:
        pass

    def cleanup(self) -> None:
        pass


class DummySessionAdapter(SessionAdapter):
    async def create_session(self, user_id: str) -> str:
        return "session"

    async def get_session(self, session_id: str):
        class DummySession:
            def __init__(self, session_id: str):
                self.session_id = session_id
        return DummySession(session_id)

    async def delete_session(self, session_id: str) -> None:
        pass

    def cleanup(self) -> None:
        pass


@pytest.mark.asyncio
async def test_generate_response_non_stream():
    service = ChatService(DummyAgentAdapter(), DummySessionAdapter())
    result = await service.generate_response("session", "hello", stream=False)
    assert result == "echo: hello"


@pytest.mark.asyncio
async def test_generate_response_stream():
    service = ChatService(DummyAgentAdapter(), DummySessionAdapter())
    stream = await service.generate_response("session", "hello", stream=True)
    chunks = [chunk async for chunk in stream]
    assert chunks == [{"data": "first"}, {"data": "second"}]

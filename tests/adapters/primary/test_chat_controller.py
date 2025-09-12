from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from typing import AsyncIterator, Any, Optional, List, Dict

from adapters.primary.chat.chat_controller import ChatController
from services.chat.chat_service import ChatService
from ports.adapters.secondary.session_adapter import SessionAdapter
from ports.adapters.secondary.mcp_agent_adapter import MCPAgentAdapter
from strands import Agent
from strands.session.repository_session_manager import RepositorySessionManager
from ports.interfaces.mcp import MCPConfig


class DummyAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id


class DummySessionAdapter(SessionAdapter):
    async def create_session(self, user_id: str) -> str:
        return "1"

    async def get_session(self, user_id: str, session_id: str):
        from conftest import DummyRepositorySessionManager
        return DummyRepositorySessionManager(session_id)

    async def get_user_session_ids(self, user_id: str) -> List[str]:
        return ["1"]

    async def list_messages(self, user_id: str, session_id: str) -> List[Any]:
        return []

    async def delete_session(self, user_id: str, session_id: str) -> None:
        pass

    async def cleanup(self) -> None:
        pass


class DummyAgentAdapter(MCPAgentAdapter):
    async def generate_response(self, agent: Agent, content: str) -> str:
        return "response"

    async def generate_stream_response(self, agent: Agent, content: str) -> AsyncIterator[Any]:
        async def iterator():
            yield {"delta": {"text": "chunk"}}
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


class FailingAgentAdapter(DummyAgentAdapter):
    async def generate_response(self, agent: Agent, content: str) -> str:
        raise RuntimeError("boom")


@pytest.fixture
def app():
    service = ChatService(DummyAgentAdapter(), DummySessionAdapter())
    controller = ChatController(service)
    app = FastAPI()
    app.include_router(controller.router)
    return app


def test_invoke_non_streaming(app):
    client = TestClient(app)
    resp = client.post("/v1/invocations", json={"message": "hi", "user_id": "user1", "session_id": "1"})
    assert resp.status_code == 200
    assert resp.json() == {"data": "response"}


def test_invoke_streaming(app):
    client = TestClient(app)
    with client.stream("POST", "/v1/invocations", json={"message": "hi", "user_id": "user1", "session_id": "1", "stream": True}) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        body = b"".join(resp.iter_bytes())
        assert b"chunk" in body


def test_invoke_requires_fields(app):
    client = TestClient(app)
    resp = client.post("/v1/invocations", json={"message": "hi"})
    assert resp.status_code == 422


def test_invoke_service_error():
    service = ChatService(FailingAgentAdapter(), DummySessionAdapter())
    controller = ChatController(service)
    fastapi_app = FastAPI()
    fastapi_app.include_router(controller.router)
    client = TestClient(fastapi_app, raise_server_exceptions=False)
    resp = client.post("/v1/invocations", json={"message": "hi", "user_id": "user1", "session_id": "1"})
    assert resp.status_code == 500

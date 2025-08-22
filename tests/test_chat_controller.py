from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from adapters.primary.chat.chat_controller import ChatController
from services.chat.chat_service import ChatService
from ports.session.session_adapter import SessionAdapter
from ports.chat.mcp_agent_adapter import MCPAgentAdapter


class DummySessionAdapter(SessionAdapter):
    async def create_session(self, user_id: str) -> str:
        return "1"

    async def get_session(self, session_id: str):
        from conftest import DummyRepositorySessionManager
        return DummyRepositorySessionManager(session_id)

    async def delete_session(self, session_id: str) -> None:
        pass

    def cleanup(self) -> None:
        pass


class DummyAgentAdapter(MCPAgentAdapter):
    async def generate_response(self, session_manager, content: str) -> str:
        return "response"

    async def generate_response_stream(self, session_manager, content: str):
        async def iterator():
            yield {"data": "chunk"}
        return iterator()

    def configure_mcp(self, mcp_config=None) -> None:
        pass

    def cleanup(self) -> None:
        pass


class FailingAgentAdapter(DummyAgentAdapter):
    async def generate_response(self, session_manager, content: str) -> str:
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
    resp = client.post("/v1/invocations", json={"message": "hi", "session_id": "1"})
    assert resp.status_code == 200
    assert resp.json() == {"data": "response"}


def test_invoke_streaming(app):
    client = TestClient(app)
    with client.stream("POST", "/v1/invocations", json={"message": "hi", "session_id": "1", "stream": True}) as resp:
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
    resp = client.post("/v1/invocations", json={"message": "hi", "session_id": "1"})
    assert resp.status_code == 500

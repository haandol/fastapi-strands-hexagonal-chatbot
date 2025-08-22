from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from adapters.primary.chat.chat_controller import ChatController


class DummyChatService:
    async def generate_response(self, session_id: str, message: str, stream: bool = False):
        if stream:
            async def iterator():
                yield {"data": "chunk"}
            return iterator()
        return "response"


def create_app():
    app = FastAPI()
    controller = ChatController(DummyChatService())
    app.include_router(controller.router)
    return app


def test_invoke_non_streaming():
    app = create_app()
    client = TestClient(app)
    resp = client.post("/v1/invocations", json={"message": "hi", "session_id": "1"})
    assert resp.status_code == 200
    assert resp.json() == {"data": "response"}


def test_invoke_streaming():
    app = create_app()
    client = TestClient(app)
    with client.stream("POST", "/v1/invocations", json={"message": "hi", "session_id": "1", "stream": True}) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        body = b"".join(resp.iter_bytes())
        assert b"chunk" in body

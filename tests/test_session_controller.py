from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from adapters.primary.session.session_controller import SessionController
from services.session.session_service import SessionService
from ports.session.session_adapter import SessionAdapter


class InMemorySessionAdapter(SessionAdapter):
    def __init__(self):
        self.sessions = {}

    async def create_session(self, user_id: str) -> str:
        session_id = f"s{len(self.sessions) + 1}"
        self.sessions[session_id] = user_id
        return session_id

    async def get_session(self, session_id: str):
        from conftest import DummyRepositorySessionManager
        if session_id not in self.sessions:
            raise KeyError(session_id)
        return DummyRepositorySessionManager(session_id)

    async def delete_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            raise KeyError(session_id)
        del self.sessions[session_id]

    def cleanup(self) -> None:
        pass


@pytest.fixture
def app():
    adapter = InMemorySessionAdapter()
    service = SessionService(adapter)
    controller = SessionController(service)
    app = FastAPI()
    app.include_router(controller.router)
    return app, adapter


def test_create_session(app):
    fastapi_app, adapter = app
    client = TestClient(fastapi_app)
    resp = client.post("/v1/sessions", json={"user_id": "u1"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    assert session_id in adapter.sessions


def test_create_session_requires_user_id(app):
    fastapi_app, _ = app
    client = TestClient(fastapi_app)
    resp = client.post("/v1/sessions", json={})
    assert resp.status_code == 422


def test_delete_session(app):
    fastapi_app, adapter = app
    adapter.sessions["s1"] = "u1"
    client = TestClient(fastapi_app)
    resp = client.request("DELETE", "/v1/sessions", json={"session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "Session deleted"}
    assert "s1" not in adapter.sessions


def test_delete_session_requires_id(app):
    fastapi_app, _ = app
    client = TestClient(fastapi_app)
    resp = client.request("DELETE", "/v1/sessions", json={})
    assert resp.status_code == 422


def test_delete_session_not_found(app):
    fastapi_app, _ = app
    client = TestClient(fastapi_app, raise_server_exceptions=False)
    resp = client.request("DELETE", "/v1/sessions", json={"session_id": "missing"})
    assert resp.status_code == 500

from fastapi import FastAPI
from fastapi.testclient import TestClient

from adapters.primary.ping.ping_controller import PingController


def create_app():
    app = FastAPI()
    controller = PingController()
    app.include_router(controller.router)
    return app


def test_ping_controller_returns_ok():
    client = TestClient(create_app())
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ping_controller_disallows_post():
    client = TestClient(create_app())
    response = client.post("/ping")
    assert response.status_code == 405

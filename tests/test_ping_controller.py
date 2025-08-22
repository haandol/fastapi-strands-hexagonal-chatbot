from fastapi import FastAPI
from fastapi.testclient import TestClient

from adapters.primary.ping.ping_controller import PingController


def test_ping_controller_returns_ok():
    controller = PingController()
    app = FastAPI()
    app.include_router(controller.router)
    client = TestClient(app)

    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

from fastapi import APIRouter

from ports.dto.ping import HealthResponse


class PingController:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/ping", self.ping, methods=["GET"])

    async def ping(self) -> HealthResponse:
        return HealthResponse(status="ok")

from typing import Dict

from fastapi import APIRouter

from services.session.session_service import SessionService
from ports.session.dto import SessionCreateRequest, SessionDeleteRequest, SessionResponse


class SessionController:
    def __init__(self, session_service: SessionService):
        self.session_service = session_service

        self.router = APIRouter(prefix="/v1")
        self.router.add_api_route(
            "/sessions",
            self.create_session,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/sessions",
            self.delete_session,
            methods=["DELETE"],
        )

    async def create_session(self, request: SessionCreateRequest) -> SessionResponse:
        session_id = await self.session_service.create_session(request.user_id)
        return SessionResponse(session_id=session_id)

    async def delete_session(self, request: SessionDeleteRequest) -> Dict[str, str]:
        await self.session_service.delete_session(request.user_id)
        return {"message": "Session deleted"}

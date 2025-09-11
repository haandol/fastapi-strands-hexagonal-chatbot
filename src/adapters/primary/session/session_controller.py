from typing import Dict

from fastapi import APIRouter

from ports.dto.session import (
    SessionCreateRequest,
    SessionDeleteRequest,
    SessionResponse,
)
from services.session.session_service import SessionService


class SessionController:
    def __init__(self, session_service: SessionService):
        self.session_service = session_service

        self.router = APIRouter(prefix="/v1/sessions")
        self.router.add_api_route(
            "",
            self.create_session,
            methods=["POST"],
            response_model=SessionResponse,
        )
        self.router.add_api_route(
            "",
            self.delete_session,
            methods=["DELETE"],
            response_model=Dict[str, str],
        )

    async def create_session(self, request: SessionCreateRequest) -> SessionResponse:
        session_id = await self.session_service.create_session(request.user_id)
        return SessionResponse(session_id=session_id)

    def delete_session(self, request: SessionDeleteRequest) -> Dict[str, str]:
        self.session_service.delete_session(request.session_id)
        return {"message": "Session deleted"}

from typing import Dict, List

from fastapi import APIRouter

from ports.dto.session import (
    SessionCreateRequest,
    SessionDeleteRequest,
    SessionResponse,
    SessionMessageResponse,
)
from services.session.session_service import SessionService


# TODO: user_id should be injected to the request via Authorization header
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
            "/user/{user_id}",
            self.list_user_sessions,
            methods=["GET"],
            response_model=List[SessionResponse],
        )
        self.router.add_api_route(
            "/{session_id}/user/{user_id}/messages",
            self.list_messages,
            methods=["GET"],
            response_model=List[SessionMessageResponse],
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

    async def list_user_sessions(self, user_id: str) -> List[SessionResponse]:
        session_ids = await self.session_service.get_user_session_ids(user_id)
        return [SessionResponse(session_id=session_id) for session_id in session_ids]

    async def list_messages(self, user_id: str, session_id: str) -> List[SessionMessageResponse]:
        messages = await self.session_service.list_messages(user_id, session_id)
        return [SessionMessageResponse(message=message) for message in messages]

    async def delete_session(self, request: SessionDeleteRequest) -> Dict[str, str]:
        await self.session_service.delete_session(request.user_id, request.session_id)
        return {"message": "Session deleted"}

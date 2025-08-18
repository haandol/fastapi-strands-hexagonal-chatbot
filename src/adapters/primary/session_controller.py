from typing import Dict

from fastapi import APIRouter

from src.ports.session_manager import SessionManager
from src.ports.dtos.responses import SessionResponse


class SessionNotFoundError(Exception):
    def __init__(self, session_id: str):
        self.session_id = session_id


class SessionController:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.router = APIRouter(prefix="/v1")

        self.router.add_api_route("/sessions/{session_id}", self.create_session, methods=["POST"])
        self.router.add_api_route("/sessions/{session_id}", self.get_session, methods=["GET"])
        self.router.add_api_route("/sessions/{session_id}", self.delete_session, methods=["DELETE"])

    async def create_session(self, session_id: str) -> SessionResponse:
        await self.session_manager.create_session(session_id)
        data = await self.session_manager.get_session_data(session_id)
        return SessionResponse(session_id=session_id, data=data)

    async def get_session(self, session_id: str) -> SessionResponse:
        data = await self.session_manager.get_session_data(session_id)
        return SessionResponse(session_id=session_id, data=data)

    async def delete_session(self, session_id: str) -> Dict[str, str]:
        await self.session_manager.delete_session(session_id)
        return {"message": "Session deleted"}

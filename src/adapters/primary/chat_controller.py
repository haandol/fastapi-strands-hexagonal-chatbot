from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.chat_service import ChatService
from ports.dtos import ChatRequest, ChatResponse


class ChatController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

        self.router = APIRouter(prefix="/v1")
        self.router.add_api_route(
            "/invocations", self.invoke, methods=["POST"])

    async def invoke(self, request: ChatRequest):
        if request.stream:
            return StreamingResponse(
                self._generate_stream_response(
                    request.session_id, request.message),
                media_type="text/event-stream",
            )
        else:
            response = await self.chat_service.invoke_async(request.session_id, request.message, request.stream)
            return ChatResponse(data=response)

    async def _generate_stream_response(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        return await self.chat_service.invoke_async(session_id, message, stream=True)

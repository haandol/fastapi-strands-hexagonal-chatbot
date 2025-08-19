from typing import AsyncIterator, Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.chat.chat_service import ChatService
from ports.chat.dto import ChatRequest, ChatResponse


class ChatController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

        self.router = APIRouter(prefix="/v1")
        self.router.add_api_route(
            "/invocations", self.invoke, methods=["POST"])

    async def invoke(self, request: ChatRequest):
        if request.stream:
            return StreamingResponse(
                self._generate_stream_response(request),
                media_type="text/event-stream",
            )
        else:
            response = await self.chat_service.generate_response(request.session_id, request.message, request.stream)
            return ChatResponse(data=response)

    async def _generate_stream_response(self, request: ChatRequest) -> AsyncIterator[Any]:
        async for event in await self.chat_service.generate_response(request.session_id, request.message, stream=True):
            if "data" in event:
                yield event["data"]

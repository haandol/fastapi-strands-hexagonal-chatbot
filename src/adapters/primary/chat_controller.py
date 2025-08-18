import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.chat_service import ChatService
from ports.dtos.requests import ChatRequest
from ports.dtos.responses import ChatResponse


class ChatController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self.router = APIRouter(prefix="/v1")
        self.router.add_api_route("/invocations", self.chat, methods=["POST"])

    async def chat(self, request: ChatRequest):
        if request.stream:
            return StreamingResponse(
                self._stream_response(request.message, request.session_id), media_type="text/event-stream"
            )
        else:
            response = await self.chat_service.process_message(request.message, request.session_id)
            return ChatResponse(data=response)

    async def _stream_response(self, message: str, session_id: str):
        response = await self.chat_service.process_message(message, session_id)

        for chunk in response.split():
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

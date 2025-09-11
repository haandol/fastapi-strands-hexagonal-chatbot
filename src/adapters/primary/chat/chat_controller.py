import json
from typing import AsyncIterator, cast

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ports.dto.chat import ChatRequest, ChatResponse
from ports.interfaces.chat import StreamChunk
from services.chat.chat_service import ChatService


class ChatController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

        self.router = APIRouter(prefix="/v1/invocations")
        self.router.add_api_route("", self.invoke, methods=["POST"])

    async def invoke(self, request: ChatRequest):
        if request.stream:
            response_stream = await self.chat_service.generate_response(
                request.session_id, request.message, stream=True
            )
            return StreamingResponse(
                self._generate_event_stream(cast(AsyncIterator[StreamChunk], response_stream)),
                media_type="text/event-stream",
            )
        else:
            response = await self.chat_service.generate_response(request.session_id, request.message, stream=False)
            return ChatResponse(data=str(response))

    async def _generate_event_stream(self, response_stream: AsyncIterator[StreamChunk]) -> AsyncIterator[str]:
        async for stream_chunk in response_stream:
            # Handle tool use events
            if "message" in stream_chunk:
                message = stream_chunk["message"]
                if message and "content" in message:
                    message_content = message["content"]
                    if isinstance(message_content, list):
                        for content in message_content:
                            if "toolUse" in content:
                                event_data = {"type": "toolUse", "data": content["toolUse"]}
                                yield f"data: {json.dumps(event_data)}\n\n"
                            elif "toolResult" in content:
                                event_data = {"type": "toolResult", "data": content["toolResult"]}
                                yield f"data: {json.dumps(event_data)}\n\n"

            # Handle text delta events
            if "delta" in stream_chunk:
                delta = stream_chunk["delta"]
                if delta and "text" in delta:
                    event_data = {"type": "textDelta", "data": delta}
                    yield f"data: {json.dumps(event_data)}\n\n"

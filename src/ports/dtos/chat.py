from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """채팅 요청 DTO"""
    message: str
    session_id: str
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """채팅 응답 DTO"""
    data: str


class ChatStreamChunk(BaseModel):
    """스트리밍 응답 청크 DTO"""
    chunk: str


class ChatStreamEnd(BaseModel):
    """스트리밍 종료 DTO"""
    done: bool = True

from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    data: str


class ChatStreamChunk(BaseModel):
    chunk: str


class ChatStreamEnd(BaseModel):
    done: bool = True

from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    data: str

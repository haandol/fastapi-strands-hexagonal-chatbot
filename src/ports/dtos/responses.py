from pydantic import BaseModel
from typing import Dict, Any


class ChatResponse(BaseModel):
    data: str


class SessionResponse(BaseModel):
    session_id: str
    data: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str

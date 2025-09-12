from pydantic import BaseModel

from strands.types.session import SessionMessage


class SessionCreateRequest(BaseModel):
    user_id: str


class SessionDeleteRequest(BaseModel):
    user_id: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str


class SessionMessageResponse(BaseModel):
    message: SessionMessage

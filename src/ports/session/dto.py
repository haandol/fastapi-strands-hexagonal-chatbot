from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    user_id: str


class SessionDeleteRequest(BaseModel):
    user_id: str


class SessionResponse(BaseModel):
    session_id: str

from pydantic import BaseModel
from typing import Dict, Any, Optional


class SessionResponse(BaseModel):
    """세션 응답 DTO"""
    session_id: str
    data: Dict[str, Any]


class SessionCreateRequest(BaseModel):
    """세션 생성 요청 DTO"""
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionUpdateRequest(BaseModel):
    """세션 업데이트 요청 DTO"""
    metadata: Dict[str, Any]

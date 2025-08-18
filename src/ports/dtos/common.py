from pydantic import BaseModel
from typing import Optional, Any, Dict


class HealthResponse(BaseModel):
    """헬스체크 응답 DTO"""
    status: str
    version: Optional[str] = None
    timestamp: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답 DTO"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginationRequest(BaseModel):
    """페이지네이션 요청 DTO"""
    page: int = 1
    size: int = 10


class PaginationResponse(BaseModel):
    """페이지네이션 응답 DTO"""
    page: int
    size: int
    total: int
    total_pages: int

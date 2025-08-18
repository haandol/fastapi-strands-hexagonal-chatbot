from fastapi import Request
from fastapi.responses import JSONResponse


class SessionNotFoundError(Exception):
    def __init__(self, session_id: str):
        self.session_id = session_id


async def session_not_found_handler(request: Request, exc: SessionNotFoundError):
    return JSONResponse(status_code=404, content={"detail": f"Session {exc.session_id} not found"})

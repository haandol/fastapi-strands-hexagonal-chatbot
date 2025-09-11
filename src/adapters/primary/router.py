from fastapi import APIRouter

from adapters.primary import (
    PingController,
    SessionController,
    ChatController,
)
from di.container import DIContainer


def create_api_router(container: DIContainer) -> APIRouter:
    """Instantiate primary adapters and set routes for FastAPI"""

    ping_controller = PingController()
    session_controller = SessionController(container.session_service)
    chat_controller = ChatController(container.chat_service)

    router = APIRouter()
    router.include_router(ping_controller.router, tags=["health"])
    router.include_router(session_controller.router, tags=["session"])
    router.include_router(chat_controller.router, tags=["chat"])

    return router

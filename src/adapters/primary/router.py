from fastapi import APIRouter

from src.adapters.primary.ping_controller import PingController
from src.adapters.primary.session_controller import SessionController
from src.adapters.primary.chat_controller import ChatController
from src.config.dependencies import Container


def create_api_router() -> APIRouter:
    container = Container()

    ping_controller = PingController()
    session_controller = SessionController(container.session_manager)
    chat_controller = ChatController(container.chat_service)

    router = APIRouter()
    router.include_router(ping_controller.router, tags=["health"])
    router.include_router(chat_controller.router, tags=["chat"])
    router.include_router(session_controller.router, tags=["sessions"])

    return router

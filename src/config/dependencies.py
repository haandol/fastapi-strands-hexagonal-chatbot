from services.chat_service import ChatService
from ports.session_manager import SessionManager
from adapters.secondary.strands_agent_manager import StrandsAgentManager
from adapters.secondary.strands_session_manager import StrandsSessionManager
from config.settings import settings


class DIContainer:
    def __init__(self):
        self._session_manager = StrandsSessionManager()
        self._agent_manager = StrandsAgentManager(
            model_id=settings.model_id,
            aws_profile_name=settings.aws_profile_name,
        )

        self._chat_service = ChatService(
            self._agent_manager,
            self._session_manager,
        )

    @property
    def chat_service(self) -> ChatService:
        return self._chat_service

    @property
    def session_manager(self) -> SessionManager:
        return self._session_manager

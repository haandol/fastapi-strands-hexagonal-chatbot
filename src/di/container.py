from services.chat_service import ChatService
from services.session_service import SessionService
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

        self._session_service = SessionService(
            self._session_manager,
        )

        self._chat_service = ChatService(
            self._agent_manager,
            self._session_manager,
        )

    @property
    def chat_service(self) -> ChatService:
        return self._chat_service

    @property
    def session_service(self) -> SessionService:
        return self._session_service

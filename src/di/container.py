from services import ChatService, SessionService
from adapters.secondary.chat import StrandsAgentAdapter
from adapters.secondary.session import StrandsFileSessionAdapter
from config import app_config


class DIContainer:
    def __init__(self):
        # secondary adapters
        self._session_adapter = StrandsFileSessionAdapter()
        self._agent_adapter = StrandsAgentAdapter(
            model_id=app_config.model_id,
            aws_profile_name=app_config.aws_profile_name,
        )

        # services
        self._session_service = SessionService(
            self._session_adapter,
        )

        self._chat_service = ChatService(
            self._agent_adapter,
            self._session_adapter,
        )

    @property
    def chat_service(self) -> ChatService:
        return self._chat_service

    @property
    def session_service(self) -> SessionService:
        return self._session_service

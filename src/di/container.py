from services import ChatService, SessionService
from adapters.secondary.chat import StrandsMCPAgentAdapter
from adapters.secondary.session import StrandsFileSessionAdapter
from ports.session import SessionAdapter
from ports.chat import AgentAdapter
from config import app_config


# TODO: resource management on DIContainer not manage by adapters (e.g. MCP clients, database connections)
class DIContainer:
    def __init__(self):
        # secondary adapters
        self._session_adapter: SessionAdapter = StrandsFileSessionAdapter()
        self._agent_adapter: AgentAdapter = StrandsMCPAgentAdapter(
            model_id=app_config.model_id,
            max_tokens=app_config.max_tokens,
            temperature=app_config.temperature,
            aws_profile_name=app_config.aws_profile_name,
        )
        self._agent_adapter.configure_mcp()

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

    def cleanup(self) -> None:
        """Cleanup all resources managed by the container"""
        if hasattr(self._agent_adapter, 'cleanup'):
            self._agent_adapter.cleanup()

        if hasattr(self._session_adapter, 'cleanup'):
            self._session_adapter.cleanup()

import asyncio
from typing import Optional

from ports.adapters.secondary import SessionAdapter
from ports.adapters.secondary import MCPAgentAdapter
from ports.adapters.secondary import O11yAdapter
from adapters.secondary.mcp_agent import StrandsMCPAgentAdapter
from adapters.secondary.session import StrandsFileSessionAdapter
from adapters.secondary.o11y import NoOpO11yAdapter, LangfuseO11yAdapter
from services.chat import ChatService
from services.session import SessionService
from config import app_config
from utils.logger import logger


class DIContainer:
    def __init__(self):
        # SECONDARY ADAPTERS
        # session
        self._session_adapter: Optional[SessionAdapter] = None
        # agent
        self._o11y_adapter: Optional[O11yAdapter] = None
        self._agent_adapter: Optional[MCPAgentAdapter] = None

        # SERVICES
        self._session_service: Optional[SessionService] = None
        self._chat_service: Optional[ChatService] = None

    @property
    def session_adapter(self) -> SessionAdapter:
        if self._session_adapter is None:
            self._session_adapter = StrandsFileSessionAdapter()
        return self._session_adapter

    @property
    def o11y_adapter(self) -> O11yAdapter:
        if app_config.tracing_enabled:
            self._o11y_adapter = LangfuseO11yAdapter()
        else:
            self._o11y_adapter = NoOpO11yAdapter()
        return self._o11y_adapter

    @property
    def agent_adapter(self) -> MCPAgentAdapter:
        if self._agent_adapter is None:
            self._agent_adapter = StrandsMCPAgentAdapter(
                model_id=app_config.model_id,
                max_tokens=app_config.max_tokens,
                temperature=app_config.temperature,
                o11y_adapter=self.o11y_adapter,
                aws_profile_name=app_config.aws_profile_name,
            )
            self._agent_adapter.configure_mcp()

        return self._agent_adapter

    @property
    def session_service(self) -> SessionService:
        if self._session_service is None:
            self._session_service = SessionService(
                session_adapter=self.session_adapter,
            )
        return self._session_service

    @property
    def chat_service(self) -> ChatService:
        if self._chat_service is None:
            self._chat_service = ChatService(
                agent_adapter=self.agent_adapter,
                session_adapter=self.session_adapter,
            )

        return self._chat_service

    async def cleanup(self) -> None:
        exceptions = await asyncio.gather(
            self.session_adapter.cleanup(),
            self.agent_adapter.cleanup(),
            return_exceptions=True,
        )
        for e in exceptions:
            if isinstance(e, Exception):
                logger.error(
                    "Error during cleanup",
                    exc=str(e),
                    exc_info=True,
                    stack_info=True,
                )

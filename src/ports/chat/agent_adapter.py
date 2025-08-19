from abc import ABC, abstractmethod
from typing import AsyncIterator, Any, Optional

from strands.session.repository_session_manager import RepositorySessionManager

from ports.mcp import MCPConfig


class AgentAdapter(ABC):
    @abstractmethod
    async def generate_response(self, session_manager: RepositorySessionManager, content: str) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, session_manager: RepositorySessionManager, content: str) -> AsyncIterator[Any]:
        pass

    @abstractmethod
    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        """Configure MCP clients and tools"""
        pass
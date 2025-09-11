from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Any, List, Dict

from strands import Agent
from strands.session.repository_session_manager import RepositorySessionManager

from ports.interfaces.mcp import MCPConfig


class MCPAgentAdapter(ABC):
    @abstractmethod
    async def generate_response(
        self,
        agent: Agent,
        content: str,
    ) -> str:
        pass

    @abstractmethod
    async def generate_stream_response(
        self,
        agent: Agent,
        content: str,
    ) -> AsyncIterator[Any]:
        pass

    @abstractmethod
    async def generate_messages(
        self,
        agent: Agent,
        content: str,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        """Configure MCP clients and tools"""
        pass

    @abstractmethod
    def get_user_preferences(self, user_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def create_agent(
        self,
        user_id: str,
        system_prompt: Optional[str] = None,
        session_manager: Optional[RepositorySessionManager] = None,
    ) -> Agent:
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

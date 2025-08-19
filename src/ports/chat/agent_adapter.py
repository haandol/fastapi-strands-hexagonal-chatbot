from abc import ABC, abstractmethod
from typing import AsyncIterator, Any, Optional, List, Callable

from ports.mcp import MCPConfig


class AgentAdapter(ABC):
    @abstractmethod
    async def generate_response(self, session_id: str, content: str) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, session_id: str, content: str) -> AsyncIterator[Any]:
        pass

    @abstractmethod
    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        """Configure MCP clients and tools"""
        pass

    @abstractmethod
    def add_tools(self, tools: List[Callable]) -> None:
        """Add additional tools to the agent"""
        pass

    @abstractmethod
    def add_hooks(self, hooks: List[Callable]) -> None:
        """Add hooks to the agent"""
        pass

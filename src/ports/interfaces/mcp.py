from typing import Union, List, Dict

from pydantic import BaseModel


class StreamableHttpMCPConfig(BaseModel):
    transportType: str = "streamable-http"
    disabled: bool = False
    url: str


class StdioMCPConfig(BaseModel):
    transportType: str = "stdio"
    disabled: bool = False
    command: str
    args: List[str]
    env: Dict[str, str] = {
        "MCP_TRANSPORT": "stdio",
    }


class MCPConfig(BaseModel):
    mcpServers: Dict[str, Union[StreamableHttpMCPConfig, StdioMCPConfig]] = {}

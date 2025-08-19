import os
import json
from typing import Optional, Dict, List, Callable

from strands.tools.mcp import MCPClient
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client

from ports.mcp import MCPConfig
from utils.logger import logger


def load_mcp_config() -> MCPConfig:
    """Load MCP configuration from default location"""
    config_path = os.path.join(os.getcwd(), "mcp_config.json")
    if not os.path.exists(config_path):
        logger.warning(
            "⚠️ MCP config file not found, using empty config", config_path=config_path)
        return MCPConfig()

    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return MCPConfig.model_validate(config_data)
    except Exception:
        logger.error("🚨 failed to load MCP config", exc_info=True, stack_info=True)
        return MCPConfig()


def initialize_mcp_clients(mcp_config: MCPConfig) -> Dict[str, MCPClient]:
    mcp_clients: Dict[str, MCPClient] = {}
    for server_name, server_config in mcp_config.mcpServers.items():
        if server_config.disabled:
            logger.info("🔄 MCP server disabled, skipping",
                        server_name=server_name)
            continue

        try:
            client: Optional[MCPClient] = None
            if server_config.transportType == "streamable-http":
                client = MCPClient(
                    lambda config=server_config: streamablehttp_client(config.url))
            elif server_config.transportType == "stdio":
                client = MCPClient(
                    lambda config=server_config: stdio_client(
                        StdioServerParameters(
                            command=config.command,
                            args=config.args,
                            env=config.env,
                        )
                    )
                )
            if client:
                mcp_clients[server_name] = client

        except Exception:
            logger.error(
                "🚨 failed to connect MCP client",
                server_name=server_name, exc_info=True, stack_info=True,
            )
    return mcp_clients


def load_mcp_tools(mcp_clients: Dict[str, MCPClient]) -> List[Callable]:
    """Load tools from MCP clients"""
    mcp_tools: List[Callable] = []
    for server_name, mcp_client in mcp_clients.items():
        try:
            client_tools = mcp_client.list_tools_sync()
            mcp_tools.extend(client_tools)
            logger.info("⚡️ MCP tools loaded", server_name=server_name,
                        tool_count=len(client_tools))
        except Exception:
            logger.error(
                "🚨 failed to load MCP tools",
                server_name=server_name, exc_info=True, stack_info=True,
            )
    return mcp_tools

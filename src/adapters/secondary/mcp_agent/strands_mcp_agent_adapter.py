from typing import (
    AsyncIterator,
    Optional,
    List,
    Dict,
    Any,
    override,
)

import boto3
from strands import Agent
from strands.hooks import HookProvider
from strands.session.repository_session_manager import RepositorySessionManager
from strands.models.bedrock import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.tools.mcp import MCPClient
from strands.tools.mcp.mcp_agent_tool import MCPAgentTool

from ports.adapters.secondary import MCPAgentAdapter
from ports.adapters.secondary import O11yAdapter
from ports.interfaces.mcp import MCPConfig
from utils.mcp import load_mcp_config, initialize_mcp_clients, load_mcp_tools
from utils.logger import logger


class StrandsMCPAgentAdapter(MCPAgentAdapter):
    def __init__(
        self,
        model_id: str,
        max_tokens: int,
        temperature: float,
        o11y_adapter: O11yAdapter,
        aws_profile_name: Optional[str] = None,
        guardrail_id: Optional[str] = None,
        guardrail_version: Optional[str] = None,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        # model region and aws_profile_name are mutually exclusive
        self.aws_profile_name = aws_profile_name
        # bedrock guardrail
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        if guardrail_id and guardrail_version:
            logger.info("🔒 using bedrock guardrail", guardrail_id=guardrail_id, guardrail_version=guardrail_version)

        self.o11y_adapter = o11y_adapter

        # Initialize model
        session = boto3.Session(
            profile_name=aws_profile_name,
        )
        self.model = BedrockModel(
            boto_session=session,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            cache_prompt="default",
            cache_tools="default",
            guardrail_id=guardrail_id,
            guardrail_version=guardrail_version,
            streaming=True,
        )

        self.conversation_manager = SlidingWindowConversationManager(
            window_size=20,
            should_truncate_results=True,
        )

        # MCP components
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_tools: List[MCPAgentTool] = []
        self.local_tools: List[Any] = []
        self.hooks: List[HookProvider] = []

    @override
    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        """Configure MCP clients and tools"""
        if mcp_config is None:
            mcp_config = load_mcp_config()

        self.mcp_clients = initialize_mcp_clients(mcp_config)

        # Start clients with error handling
        for server_name, client in self.mcp_clients.items():
            logger.info("🚀 Connecting MCP client", server_name=server_name)
            try:
                client.start()
                logger.info("⚡️ MCP client connected", server_name=server_name)
            except Exception as e:
                logger.error("⚠️ Failed to start MCP client", server_name=server_name, exc_info=True)
                raise e

        self.mcp_tools = load_mcp_tools(self.mcp_clients)

    @override
    def get_user_preferences(self, user_id: str) -> Optional[str]:
        mcp_client = self.mcp_clients.get("mem0-memory", None)
        if mcp_client is None:
            logger.warn("🚨 mem0 client not found", mcp_clients=self.mcp_clients)
            return ""
        tool_result = mcp_client.call_tool_sync(
            f"initial-memory-${user_id}",
            "mem0_memory",
            {
                "action": "list",
                "user_id": user_id,
            },
        )
        structured_tool_result = tool_result.get("structuredContent")
        if structured_tool_result is None:
            return ""

        results = structured_tool_result.get("data", {}).get("results", [])
        logger.debug("📝 user preferences", user_id=user_id, results=results)
        return "\n".join(
            [f" <preference created_at={result['created_at']}>{result['memory']}</preference>" for result in results]
        )

    @override
    def create_agent(
        self,
        user_id: str,
        system_prompt: Optional[str] = None,
        session_manager: Optional[RepositorySessionManager] = None,
    ) -> Agent:
        trace_attributes = self.o11y_adapter.create_trace_attributes(
            agent_name="StrandsMCPAgent",
            user_id=user_id,
        )

        logger.info(
            "🤖 creating StrandsAgent for the session",
            user_id=user_id,
            session_id=session_manager.session_id if session_manager else None,
        )
        return Agent(
            model=self.model,
            tools=self.mcp_tools + self.local_tools,
            system_prompt=system_prompt,
            conversation_manager=self.conversation_manager,
            hooks=self.hooks,
            session_manager=session_manager,
            trace_attributes=trace_attributes,
        )

    @override
    async def generate_response(
        self,
        agent: Agent,
        content: str,
    ) -> str:
        result = await agent.invoke_async(prompt=content)
        content_block = result.message["content"][0]
        return content_block.get("text", "")

    @override
    async def generate_stream_response(
        self,
        agent: Agent,
        content: str,
    ) -> AsyncIterator[Any]:
        return agent.stream_async(prompt=content)

    @override
    async def generate_messages(self, agent: Agent, content: str) -> List[Dict[str, Any]]:
        """Generate messages for creating semantic cache messages"""
        messages: List[Dict[str, Any]] = []
        async for chunk in agent.stream_async(prompt=content):
            if "message" in chunk:
                messages.append(chunk)
        return messages

    @override
    async def cleanup(self) -> None:
        logger.info("🧹 cleaning up agent adapter")
        for client_name, client in self.mcp_clients.items():
            try:
                logger.info("🔌 closing MCP client", client_name=client_name)
                client.stop(None, None, None)
            except Exception:
                logger.error(
                    "🚨 error on closing MCP client",
                    client_name=client_name,
                    exc_info=True,
                    stack_info=True,
                )

        await self.o11y_adapter.cleanup()

        self.mcp_clients.clear()
        self.mcp_tools.clear()

        logger.info("🧹 agent adapter cleaned up")

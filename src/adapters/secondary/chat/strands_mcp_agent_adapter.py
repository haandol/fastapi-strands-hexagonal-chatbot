from typing import AsyncIterator, Any, Optional, List, Callable, Dict

import boto3
from strands import Agent
from strands.session.repository_session_manager import RepositorySessionManager
from strands.models.bedrock import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.tools.mcp import MCPClient, MCPAgentTool

from adapters.secondary.chat.prompt import SYSTEM_PROMPT
from ports.chat import AgentAdapter
from ports.mcp import MCPConfig
from utils.mcp import load_mcp_config, initialize_mcp_clients, load_mcp_tools
from utils.logger import logger


class StrandsMCPAgentAdapter(AgentAdapter):
    def __init__(
        self,
        model_id: str,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        aws_profile_name: Optional[str] = None,
        model_region: Optional[str] = None,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        # model region and aws_profile_name are mutually exclusive
        self.aws_profile_name = aws_profile_name
        self.model_region = model_region if not aws_profile_name else None
        self.system_prompt = SYSTEM_PROMPT

        # Initialize model
        session = boto3.Session(
            profile_name=aws_profile_name,
            region_name=model_region,
        )
        self.model = BedrockModel(
            boto_session=session,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            cache_prompt="default",
            cache_tools="default",
            streaming=True,
        )

        self.conversation_manager = SlidingWindowConversationManager(
            window_size=20,
            should_truncate_results=True,
        )

        # MCP components
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_tools: List[MCPAgentTool] = []
        self.local_tools: List[Callable] = []
        self.hooks: List[Callable] = []

        # Agent instances per session
        self.agents: Dict[str, Agent] = {}

    def shutdown(self) -> None:
        """Public method to initiate shutdown"""
        logger.info("🛑 shutdown requested")
        self.cleanup()

    def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
        """Configure MCP clients and tools"""
        if mcp_config is None:
            mcp_config = load_mcp_config()

        self.mcp_clients = initialize_mcp_clients(mcp_config)

        for server_name, client in self.mcp_clients.items():
            client.__enter__()
            logger.info("⚡️ MCP client connected", server_name=server_name)

        self.mcp_tools = load_mcp_tools(self.mcp_clients)

    def _get_or_create_agent(self, session_id: str) -> Agent:
        """Get existing agent or create new one for session"""
        if session_id in self.agents:
            logger.info("🔄 reusing existing agent for session",
                        session_id=session_id)
            return self.agents[session_id]

        agent = Agent(
            model=self.model,
            conversation_manager=self.conversation_manager,
            system_prompt=self.system_prompt,
            tools=self.mcp_tools + self.local_tools,
            hooks=self.hooks,
        )
        self.agents[session_id] = agent
        logger.info("🤖 StrandsAgent created for session",
                    session_id=session_id)
        return agent

    async def generate_response(self, session_manager: RepositorySessionManager, content: str) -> str:
        """Generate response using the agent"""
        session_id = session_manager.session_id
        agent = self._get_or_create_agent(session_id)

        response = await agent.invoke_async(prompt=content)
        content_block = response.message["content"][0]
        return content_block["text"]

    async def generate_response_stream(self, session_manager: RepositorySessionManager, content: str) -> AsyncIterator[Any]:
        """Generate streaming response using the agent"""
        session_id = session_manager.session_id
        agent = self._get_or_create_agent(session_id)

        return agent.stream_async(prompt=content)

    def cleanup(self) -> None:
        logger.info("🧹 cleaning up agent adapter")

        for client_name, client in self.mcp_clients.items():
            try:
                logger.info("🔌 closing MCP client", client_name=client_name)
                client.__exit__(None, None, None)
            except Exception:
                logger.error(
                    "🚨 error on closing MCP client",
                    client_name=client_name, exc_info=True, stack_info=True,
                )

        self.mcp_clients.clear()
        self.mcp_tools.clear()
        self.agents.clear()

        logger.info("🧹 agent adapter cleaned up")

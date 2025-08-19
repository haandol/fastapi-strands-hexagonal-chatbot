from typing import AsyncIterator, Any, Optional, List, Callable, Dict
import signal
import atexit

import boto3
from strands import Agent
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

        # Setup cleanup handlers
        # TODO: resource management on adapters not manage by DIContainer (e.g. MCP clients, database connections)
        self._setup_cleanup_handlers()

    def _setup_cleanup_handlers(self) -> None:
        """Setup signal handlers and atexit for cleanup"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Register atexit handler as backup
        atexit.register(self.cleanup)

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        logger.info(f"📡 received signal {signal_name}, initiating cleanup...")
        self.cleanup()
        # Re-raise the signal to allow normal termination
        signal.signal(signum, signal.SIG_DFL)
        signal.raise_signal(signum)

    def cleanup(self) -> None:
        """Explicit cleanup method for MCP clients and resources"""
        logger.info("🧹 cleaning up MCP clients...")

        # Cleanup MCP clients
        for client_name, client in self.mcp_clients.items():
            try:
                logger.info(f"🔌 closing MCP client: {client_name}")
                client.__exit__(None, None, None)
            except Exception as e:
                logger.error(
                    f"🚨 error on closing MCP client {client_name}", error=str(e))

        # Clear all collections
        self.mcp_clients.clear()
        self.mcp_tools.clear()
        self.agents.clear()

        logger.info("🧹 MCP clients cleaned up")

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

    def add_tools(self, tools: List[Callable]) -> None:
        self.local_tools.extend(tools)

    def add_hooks(self, hooks: List[Callable]) -> None:
        self.hooks.extend(hooks)

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

    async def generate_response(self, session_id: str, content: str) -> str:
        """Generate response using the agent"""
        agent = self._get_or_create_agent(session_id)
        response = await agent.invoke_async(prompt=content)
        content_block = response.message["content"][0]
        return content_block["text"]

    async def generate_response_stream(self, session_id: str, content: str) -> AsyncIterator[Any]:
        """Generate streaming response using the agent"""
        agent = self._get_or_create_agent(session_id)
        return agent.stream_async(prompt=content)

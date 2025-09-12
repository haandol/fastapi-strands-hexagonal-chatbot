from typing import AsyncIterator, Union, Any, Dict

from strands import Agent

from ports.adapters.secondary import MCPAgentAdapter
from ports.adapters.secondary import SessionAdapter
from services.chat.prompt import SYSTEM_PROMPT
from utils.logger import logger


class ChatService:
    def __init__(
        self,
        agent_adapter: MCPAgentAdapter,
        session_adapter: SessionAdapter,
    ):
        self._agent_adapter = agent_adapter
        self._session_adapter = session_adapter

        # Agent instances per session
        self.session_agents: Dict[str, Agent] = {}

    async def _get_or_create_agent(self, user_id: str, session_id: str):
        if session_id not in self.session_agents:
            session_manager = await self._session_adapter.get_session(user_id, session_id)

            self.session_agents[session_id] = self._agent_adapter.create_agent(
                user_id=user_id,
                system_prompt=SYSTEM_PROMPT,
                session_manager=session_manager,
            )
            logger.info(
                "🤖 StrandsAgent has been created for the user session",
                user_id=user_id,
                session_id=session_id,
            )
        return self.session_agents[session_id]

    async def generate_response(
        self,
        user_id: str,
        session_id: str,
        prompt: str,
        stream: bool = False,
    ) -> Union[str, AsyncIterator[Any]]:
        agent = await self._get_or_create_agent(user_id, session_id)

        if stream:
            return await self._agent_adapter.generate_stream_response(agent, prompt)
        else:
            return await self._agent_adapter.generate_response(agent, prompt)

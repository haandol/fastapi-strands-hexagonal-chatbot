from typing import AsyncIterator, Any, Optional

from strands import Agent
from strands.models.bedrock import BedrockModel

from ports.agent_manager import AgentManager


class StrandsAgentManager(AgentManager):
    def __init__(self, model_id: str, aws_profile_name: Optional[str] = None):
        model = BedrockModel(
            model_id=model_id,
            aws_profile_name=aws_profile_name,
            streaming=True,
        )
        self.agent: Agent = Agent(model=model)

    async def generate_response(self, session_id: str, content: str) -> str:
        response = await self.agent.invoke_async(prompt=content)
        content = response.message["content"][0]
        return content["text"]

    async def generate_response_stream(self, session_id: str, content: str) -> AsyncIterator[Any]:
        return self.agent.stream_async(prompt=content)

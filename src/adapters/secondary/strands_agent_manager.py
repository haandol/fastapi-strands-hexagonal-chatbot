from typing import Optional

from strands import Agent
from strands.models.bedrock import BedrockModel

from ports.agent_manager import AgentManager


class StrandsAgentManager(AgentManager):
    def __init__(self, model_id: str, aws_profile_name: Optional[str] = None):
        model = BedrockModel(
            model_id=model_id,
            aws_profile_name=aws_profile_name,
            # cache_prompt="default",
            # cache_tools="default",
        )
        self.agent = Agent(model=model)

    async def generate_response(self, content: str) -> str:
        response = await self.agent.invoke_async(prompt=content)
        content = response.message["content"][0]
        return content["text"]

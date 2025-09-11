from typing import Dict, Any, override

from ports.adapters.secondary import O11yAdapter
from utils.logger import logger


class NoOpO11yAdapter(O11yAdapter):
    def __init__(self):
        logger.info("🚫 Observability disabled")

    @override
    def create_trace_attributes(
        self,
        agent_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        return {}

    @override
    async def cleanup(self):
        logger.info("✅ NoOp Observability shutdown completed")

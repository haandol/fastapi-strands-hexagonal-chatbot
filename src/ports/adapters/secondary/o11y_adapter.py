from abc import ABC, abstractmethod
from typing import Dict, Any


class O11yAdapter(ABC):
    @abstractmethod
    def create_trace_attributes(self, agent_name: str, **kwarg) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

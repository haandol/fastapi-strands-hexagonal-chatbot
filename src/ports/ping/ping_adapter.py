from abc import ABC, abstractmethod


class PingAdapter(ABC):
    @abstractmethod
    async def ping(self) -> str:
        pass

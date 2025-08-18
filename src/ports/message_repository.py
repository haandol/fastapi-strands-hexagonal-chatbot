from typing import List
from abc import ABC, abstractmethod

from src.domain.entities.message import Message


class MessageRepository(ABC):
    @abstractmethod
    async def save(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def get_by_session(self, session_id: str) -> List[Message]:
        pass

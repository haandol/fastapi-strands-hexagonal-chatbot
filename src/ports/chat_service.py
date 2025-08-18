from typing import List
from abc import ABC, abstractmethod

from src.domain.entities.message import Message


class ChatService(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[Message]) -> str:
        pass

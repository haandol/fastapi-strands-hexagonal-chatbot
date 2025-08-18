from typing import Dict, Any

from strands.session.file_session_manager import FileSessionManager

from src.ports.session_manager import SessionManager


class StrandsSessionManager(SessionManager):
    def __init__(self, base_path: str = "./sessions"):
        self.base_path = base_path

    async def create_session(self, session_id: str) -> None:
        self.file_session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir=self.base_path,
        )

    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        return self.file_session_manager.get_session_data(session_id)

    async def update_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        self.file_session_manager.update_session_data(session_id, data)

    async def delete_session(self, session_id: str) -> None:
        self.file_session_manager.delete_session(session_id)

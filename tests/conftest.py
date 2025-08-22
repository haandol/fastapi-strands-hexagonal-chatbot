import os
import sys
from types import SimpleNamespace

os.environ.setdefault("MODEL_ID", "test-model")
os.environ.setdefault("ENVIRONMENT", "test")

class DummyRepositorySessionManager:
    def __init__(self, session_id: str, **kwargs):
        self.session_id = session_id

class DummyFileSessionManager(DummyRepositorySessionManager):
    def __init__(self, session_id: str, storage_dir: str, **kwargs):
        super().__init__(session_id, **kwargs)
        self.storage_dir = storage_dir

sys.modules.setdefault(
    "strands.session.repository_session_manager",
    SimpleNamespace(RepositorySessionManager=DummyRepositorySessionManager),
)
sys.modules.setdefault(
    "strands.session.file_session_manager",
    SimpleNamespace(FileSessionManager=DummyFileSessionManager),
)

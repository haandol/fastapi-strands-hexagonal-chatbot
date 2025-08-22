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


class DummySession:
    def __init__(self, profile_name=None, region_name=None):
        self.profile_name = profile_name
        self.region_name = region_name


class DummyBedrockModel:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs


class DummySlidingWindowConversationManager:
    def __init__(self, *args, **kwargs):
        pass


class DummyMCPClient:
    def __init__(self):
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self, *args, **kwargs):
        self.stopped = True


class DummyAgent:
    def __init__(self, *args, **kwargs):
        pass

    async def invoke_async(self, prompt: str):
        return SimpleNamespace(message={"content": [{"text": "dummy"}]})
    def stream_async(self, prompt: str):
        async def iterator():
            yield {"data": "chunk"}

        return iterator()

sys.modules.setdefault(
    "strands.session.repository_session_manager",
    SimpleNamespace(RepositorySessionManager=DummyRepositorySessionManager),
)
sys.modules.setdefault(
    "strands.session.file_session_manager",
    SimpleNamespace(FileSessionManager=DummyFileSessionManager),
)

# Stub out external dependencies used by adapters
sys.modules.setdefault(
    "boto3",
    SimpleNamespace(Session=DummySession, client=lambda *args, **kwargs: None),
)
sys.modules.setdefault(
    "strands.models.bedrock", SimpleNamespace(BedrockModel=DummyBedrockModel)
)
sys.modules.setdefault(
    "strands.agent.conversation_manager",
    SimpleNamespace(SlidingWindowConversationManager=DummySlidingWindowConversationManager),
)
sys.modules.setdefault(
    "strands.tools.mcp", SimpleNamespace(MCPClient=DummyMCPClient)
)

class _DummyStructlog(SimpleNamespace):
    def __init__(self):
        processors = SimpleNamespace(
            add_log_level=None,
            TimeStamper=lambda fmt=None: None,
            StackInfoRenderer=lambda: None,
            format_exc_info=None,
            UnicodeDecoder=None,
            dict_tracebacks=None,
            JSONRenderer=lambda: None,
        )
        dev = SimpleNamespace(
            set_exc_info=None,
            ConsoleRenderer=lambda colors=True: None,
        )

        super().__init__(
            processors=processors,
            dev=dev,
            configure=lambda **kwargs: None,
            PrintLoggerFactory=lambda: None,
            BoundLogger=object,
            get_logger=lambda name=None: SimpleNamespace(),
        )


sys.modules.setdefault("structlog", _DummyStructlog())

# Additional stubs for optional dependencies
sys.modules.setdefault("strands", SimpleNamespace(Agent=DummyAgent))
sys.modules.setdefault("strands.hooks", SimpleNamespace(HookProvider=object))
sys.modules.setdefault("dotenv", SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))
sys.modules.setdefault(
    "utils.logger",
    SimpleNamespace(
        logger=SimpleNamespace(
            info=lambda *args, **kwargs: None,
            error=lambda *args, **kwargs: None,
            warning=lambda *args, **kwargs: None,
        )
    ),
)

sys.modules.setdefault(
    "utils.mcp",
    SimpleNamespace(
        load_mcp_config=lambda: {},
        initialize_mcp_clients=lambda config: {},
        load_mcp_tools=lambda clients: [],
    ),
)

# Stub primary router to avoid importing DI container and secondary adapters
sys.modules.setdefault("adapters.primary.router", SimpleNamespace(create_api_router=lambda *args, **kwargs: None))

# Ensure ulid module provides callable ulid() helper
try:
    import ulid as _ulid  # type: ignore
    if not callable(getattr(_ulid, "ulid", None)):
        _ulid.ulid = _ulid.new  # type: ignore[attr-defined]
except Exception:
    pass

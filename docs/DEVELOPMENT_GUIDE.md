# Development Guide

This guide helps developers understand and modify the codebase following hexagonal architecture principles.

## Architecture Overview

The application follows hexagonal architecture with clear separation between:
- **Ports**: Interfaces defining contracts
- **Adapters**: Implementations of ports
- **Services**: Business logic
- **DI Container**: Dependency management

## Code Structure

```
src/
├── ports/              # Interfaces (contracts)
├── adapters/           # Implementations
│   ├── primary/        # Inbound (REST controllers)
│   └── secondary/      # Outbound (external services)
├── services/           # Business logic
├── di/                 # Dependency injection
├── config/             # Configuration
└── utils/              # Utilities
```

## Common Development Tasks

### 1. Adding a New API Endpoint

#### Step 1: Define the Port (Interface)
```python
# src/ports/example/example_adapter.py
from abc import ABC, abstractmethod
from .dto import ExampleRequest, ExampleResponse

class ExampleAdapter(ABC):
    @abstractmethod
    async def process_example(self, request: ExampleRequest) -> ExampleResponse:
        pass
```

#### Step 2: Create DTOs
```python
# src/ports/example/dto.py
from pydantic import BaseModel

class ExampleRequest(BaseModel):
    data: str

class ExampleResponse(BaseModel):
    result: str
```

#### Step 3: Implement the Service
```python
# src/services/example/example_service.py
from ports.example import ExampleAdapter, ExampleRequest, ExampleResponse

class ExampleService:
    def __init__(self, example_adapter: ExampleAdapter):
        self._example_adapter = example_adapter

    async def handle_example(self, request: ExampleRequest) -> ExampleResponse:
        return await self._example_adapter.process_example(request)
```

#### Step 4: Create the Controller
```python
# src/adapters/primary/example/example_controller.py
from fastapi import APIRouter
from services.example import ExampleService
from ports.example.dto import ExampleRequest, ExampleResponse

class ExampleController:
    def __init__(self, example_service: ExampleService):
        self.example_service = example_service
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/example", response_model=ExampleResponse)
        async def process_example(self, request: ExampleRequest):
            return await self.example_service.handle_example(request)
```

#### Step 5: Implement Secondary Adapter
```python
# src/adapters/secondary/example/example_adapter_impl.py
from ports.example import ExampleAdapter, ExampleRequest, ExampleResponse

class ExampleAdapterImpl(ExampleAdapter):
    async def process_example(self, request: ExampleRequest) -> ExampleResponse:
        # Implementation logic here
        return ExampleResponse(result=f"Processed: {request.data}")
```

#### Step 6: Wire in DI Container
```python
# src/di/container.py
from services.example import ExampleService
from adapters.secondary.example import ExampleAdapterImpl

class DIContainer:
    def __init__(self):
        # ... existing code ...

        # Add new adapter and service
        self._example_adapter = ExampleAdapterImpl()
        self._example_service = ExampleService(self._example_adapter)

    @property
    def example_service(self) -> ExampleService:
        return self._example_service
```

#### Step 7: Add to Router
```python
# src/adapters/primary/router.py
from adapters.primary.example import ExampleController

def create_api_router(container: DIContainer) -> APIRouter:
    # ... existing controllers ...
    example_controller = ExampleController(container.example_service)

    router = APIRouter()
    # ... existing routes ...
    router.include_router(example_controller.router, tags=["example"])

    return router
```

### 2. Adding New MCP Tools

#### Step 1: Configure MCP Server
```json
// mcp_config.json
{
  "mcpServers": {
    "my-custom-server": {
      "transportType": "streamable-http",
      "url": "https://my-server.com/mcp"
    }
  }
}
```

#### Step 2: Add Local Tools (Optional)
```python
# src/adapters/secondary/chat/strands_mcp_agent_adapter.py
def configure_mcp(self, mcp_config: Optional[MCPConfig] = None) -> None:
    # ... existing MCP setup ...

    # Add custom local tools
    self.local_tools.append(my_custom_tool)
```

### 3. Modifying Business Logic

#### Update Service Layer
```python
# src/services/chat/chat_service.py
class ChatService:
    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        # Add your business logic here
        # Example: preprocessing, validation, post-processing

        # Validate input
        if not request.message.strip():
            raise ValueError("Message cannot be empty")

        # Generate response using agent
        response = await self._agent_adapter.generate_response(
            session_manager, request.message
        )

        # Post-process response
        processed_response = self._post_process(response)

        return ChatResponse(content=processed_response)
```

### 4. Adding Configuration

#### Step 1: Update Config Model
```python
# src/config/app.py
class AppConfig:
    # ... existing fields ...
    new_feature_enabled: bool = False
    new_feature_timeout: int = 30
```

#### Step 2: Update Environment File
```env
# env/local.env
NEW_FEATURE_ENABLED=true
NEW_FEATURE_TIMEOUT=60
```

### 5. Adding Middleware

#### Step 1: Create Middleware
```python
# src/adapters/primary/middleware/example_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class ExampleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pre-processing
        response = await call_next(request)
        # Post-processing
        return response
```

#### Step 2: Add to Application
```python
# src/main.py
def create_app() -> FastAPI:
    app = FastAPI(...)

    # Add middleware
    app.add_middleware(ExampleMiddleware)

    return app
```

## Testing Guidelines

### Unit Tests
```python
# tests/services/test_chat_service.py
import pytest
from unittest.mock import Mock
from services.chat import ChatService

@pytest.fixture
def mock_agent_adapter():
    return Mock()

@pytest.fixture
def chat_service(mock_agent_adapter):
    return ChatService(mock_agent_adapter, Mock())

async def test_generate_response(chat_service, mock_agent_adapter):
    # Arrange
    mock_agent_adapter.generate_response.return_value = "test response"

    # Act
    result = await chat_service.generate_response(request)

    # Assert
    assert result.content == "test response"
```

### Integration Tests
```python
# tests/integration/test_chat_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/v1/invocations", json={
        "message": "Hello",
        "session_id": "test_session"
    })
    assert response.status_code == 200
```

## Best Practices

### 1. Follow Hexagonal Architecture
- Keep business logic in services
- Use ports for abstractions
- Implement adapters for external dependencies

### 2. Dependency Injection
- Register all dependencies in DIContainer
- Use constructor injection
- Avoid service locator pattern

### 3. Error Handling
```python
# Use structured logging
from utils.logger import logger

try:
    result = await some_operation()
except Exception as e:
    logger.error("Operation failed", error=str(e), exc_info=True)
    raise
```

### 4. Configuration
- Use environment variables for configuration
- Validate configuration at startup
- Use type hints for config models

### 5. Resource Management
- Implement cleanup methods for adapters
- Use context managers for resources
- Register cleanup in DI container

## Debugging Tips

### 1. Enable Debug Logging
```python
# src/utils/logger.py
import structlog

logger = structlog.get_logger()
logger.setLevel("DEBUG")  # For development
```

### 2. MCP Debugging
```bash
# Check MCP server connectivity
curl -X POST https://knowledge-mcp.global.api.aws/mcp

# Validate MCP config
python -c "
from utils.mcp import load_mcp_config
config = load_mcp_config()
print(config)
"
```

### 3. Session Debugging
```bash
# Check session files
ls -la .sessions/
cat .sessions/session_*/session.json
```

## Common Pitfalls

1. **Circular Dependencies**: Avoid importing services in adapters
2. **Resource Leaks**: Always implement cleanup methods
3. **Tight Coupling**: Use interfaces, not concrete implementations
4. **Missing Error Handling**: Always handle exceptions gracefully
5. **Configuration Issues**: Validate environment variables at startup

## Getting Help

1. Check existing implementations for patterns
2. Review the hexagonal architecture principles
3. Use structured logging for debugging
4. Write tests for new functionality
5. Follow the existing code style and patterns

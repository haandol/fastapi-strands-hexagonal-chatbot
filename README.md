# FastAPI Strands Hexagonal Chatbot

A FastAPI-based chatbot application built with hexagonal architecture and powered by AWS Bedrock through the Strands framework with MCP (Model Context Protocol) support.

## Architecture

This project implements hexagonal architecture (ports and adapters pattern) with the following structure:

```
src/
├── adapters/           # External interfaces
│   ├── primary/        # Inbound adapters (REST API controllers)
│   │   ├── chat/
│   │   │   └── chat_controller.py
│   │   ├── session/
│   │   │   └── session_controller.py
│   │   ├── ping/
│   │   │   └── ping_controller.py
│   │   ├── __init__.py
│   │   └── router.py
│   └── secondary/      # Outbound adapters (Strands implementations)
│       ├── chat/
│       │   ├── strands_mcp_agent_adapter.py
│       │   ├── prompt.py
│       │   └── __init__.py
│       └── session/
│           ├── strands_file_session_adapter.py
│           └── __init__.py
├── ports/              # Interface definitions (ports)
│   ├── chat/
│   │   ├── agent_adapter.py
│   │   └── dto.py
│   ├── session/
│   │   ├── session_adapter.py
│   │   └── dto.py
│   ├── ping/
│   │   ├── ping_adapter.py
│   │   └── dto.py
│   └── mcp/
│       ├── config.py
│       └── __init__.py
├── services/           # Application services
│   ├── chat/
│   │   └── chat_service.py
│   ├── session/
│   │   └── session_service.py
│   └── __init__.py
├── di/                 # Dependency injection
│   ├── __init__.py
│   └── container.py
├── config/             # Configuration
│   ├── __init__.py
│   └── app.py
├── utils/              # Utilities
│   ├── logger.py
│   └── mcp.py
└── main.py             # Application entry point
```

## Features

- **RESTful API** with FastAPI
- **Hexagonal Architecture** for clean separation of concerns
- **AWS Bedrock Integration** via Strands framework
- **MCP (Model Context Protocol) Support** for extensible tool integration
- **Session Management** with file-based persistence
- **Streaming Support** for real-time chat responses
- **Health Check** endpoint
- **Structured Logging** with structlog

## Quick Start

### Prerequisites

- Python 3.13+
- AWS credentials configured
- Access to AWS Bedrock Claude models

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd fastapi-strands-hexagonal-chatbot
```

2. Install dependencies:

```bash
uv sync
```

3. Configure environment variables:

```bash
cp env/local.env .env
# Edit .env with your settings
```

### Configuration

#### Environment Variables

Create a `.env` file with the following variables:

```env
MODEL_ID="us.anthropic.claude-sonnet-4-20250514-v1:0"
MODEL_TEMPERATURE="0.3"
MODEL_MAX_TOKENS="2048"
# AWS_PROFILE_NAME="default"  # Optional
ENVIRONMENT="local"
```

#### MCP Configuration

Configure MCP servers in `mcp_config.json`:

```json
{
  "mcpServers": {
    "aws-knowledge-mcp-server": {
      "transportType": "streamable-http",
      "url": "https://knowledge-mcp.global.api.aws"
    },
    "context7": {
      "transportType": "streamable-http",
      "disabled": true,
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

Environment-specific configurations are also supported in `mcp_config/`:
- `mcp_config/local.json`
- `mcp_config/dev.json`

### Running the Application

#### Local Development

```bash
uv run src/main.py
```

#### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t chatbot .
docker run -p 8000:8000 -v ~/.aws:/root/.aws chatbot
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```http
GET /ping
```

### Chat

```http
POST /v1/invocations
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "session_id": "session_123",
  "stream": false
}
```

### Session Management

```http
POST /v1/sessions/{session_id}
GET /v1/sessions/{session_id}
DELETE /v1/sessions/{session_id}
```

## Project Structure

### Core Components

- **ChatService**: Orchestrates chat interactions between agents and sessions
- **SessionService**: Manages session lifecycle and persistence
- **Controllers**: Handle HTTP requests and responses
- **DIContainer**: Manages dependency injection and service wiring

### Adapters

#### Primary Adapters (Inbound)

- `ChatController`: REST API for chat interactions at `/v1/invocations`
- `SessionController`: REST API for session management at `/v1/sessions`
- `PingController`: Health check endpoint at `/ping`

#### Secondary Adapters (Outbound)

- `StrandsMCPAgentAdapter`: AWS Bedrock and MCP integration via Strands framework
- `StrandsFileSessionAdapter`: File-based session storage implementation via Strands framework

### Ports (Interfaces)

- `AgentAdapter`: Interface for AI model interactions with MCP support
- `SessionAdapter`: Interface for session persistence
- DTOs: Data transfer objects for each domain (chat, session, ping)
- MCP Configuration: Models for MCP server configuration

### MCP Integration

The application supports MCP (Model Context Protocol) through the `StrandsMCPAgentAdapter`, which:

- Loads MCP server configurations from `mcp_config.json` or environment-specific files
- Initializes MCP clients for configured servers
- Provides tools from MCP servers to the AI agent
- Supports both `stdio` and `streamable-http` transport types

For detailed MCP usage, see [docs/MCP_USAGE.md](docs/MCP_USAGE.md).

## Dependencies

- **FastAPI**: Web framework
- **Strands**: AI agent framework with AWS Bedrock and MCP support
- **Structlog**: Structured logging
- **Python-dotenv**: Environment variable management
- **ULID**: Unique identifier generation
- **Uvicorn**: ASGI server

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

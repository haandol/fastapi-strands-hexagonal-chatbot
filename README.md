# FastAPI Strands Hexagonal Chatbot

A FastAPI-based chatbot application built with hexagonal architecture and powered by AWS Bedrock through the Strands framework.

## Architecture

This project implements hexagonal architecture (ports and adapters pattern) with the following structure:

```
src/
├── adapters/           # External interfaces
│   ├── primary/        # Inbound adapters (REST API controllers)
│   │   ├── chat_controller.py
│   │   ├── session_controller.py
│   │   ├── ping_controller.py
│   │   └── router.py
│   └── secondary/      # Outbound adapters (Strands implementations)
│       ├── strands_agent_manager.py
│       └── strands_session_manager.py
├── ports/              # Interface definitions
│   ├── agent_manager.py
│   ├── session_manager.py
│   ├── chat_service.py
│   ├── message_repository.py
│   └── dtos/           # Data Transfer Objects
│       ├── __init__.py
│       ├── chat.py
│       ├── session.py
│       └── common.py
├── services/           # Application services
│   └── chat_service.py
├── config/             # Configuration and dependencies
│   ├── settings.py
│   └── dependencies.py
├── utils/              # Utilities
│   └── logger.py
└── main.py             # Application entry point
```

## Features

- **RESTful API** with FastAPI
- **Hexagonal Architecture** for clean separation of concerns
- **AWS Bedrock Integration** via Strands framework
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

Create a `.env` file with the following variables:

```env
MODEL_ID="us.anthropic.claude-sonnet-4-20250514-v1:0"
MODEL_TEMPERATURE="0.3"
MODEL_MAX_TOKENS="2048"
# AWS_PROFILE_NAME="default"  # Optional
ENVIRONMENT="local"
```

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
- **AgentManager**: Interface for AI model interactions via Strands
- **SessionManager**: Interface for conversation persistence
- **Controllers**: Handle HTTP requests and responses

### Adapters

#### Primary Adapters (Inbound)

- `ChatController`: REST API for chat interactions at `/v1/invocations`
- `SessionController`: REST API for session management at `/v1/sessions`
- `PingController`: Health check endpoint at `/ping`

#### Secondary Adapters (Outbound)

- `StrandsAgentManager`: AWS Bedrock integration via Strands
- `StrandsSessionManager`: File-based session storage

### Ports (Interfaces)

- `AgentManager`: Interface for AI model interactions
- `SessionManager`: Interface for session persistence
- `ChatService`: Interface for chat orchestration
- `MessageRepository`: Interface for message storage

## Dependencies

- **FastAPI**: Web framework
- **Strands**: AI agent framework with AWS Bedrock support
- **Pydantic**: Data validation (included with FastAPI)
- **Structlog**: Structured logging
- **Python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

# FastAPI Strands Hexagonal Chatbot

A FastAPI-based chatbot application built with hexagonal architecture and powered by AWS Bedrock through the Strands framework.

## Architecture

This project implements hexagonal architecture (ports and adapters pattern) with the following structure:

```
src/
├── adapters/           # External interfaces
│   ├── primary/        # Inbound adapters (REST API)
│   └── secondary/      # Outbound adapters (Strands, File storage)
├── domain/             # Business entities
├── ports/              # Interface definitions
├── services/           # Application services
├── config/             # Configuration and dependencies
└── utils/              # Utilities
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
AWS_PROFILE_NAME="default"  # Optional
ENVIRONMENT="local"
```

### Running the Application

```bash
uv run main.py
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
POST /sessions/{session_id}
GET /sessions/{session_id}
DELETE /sessions/{session_id}
```

## Project Structure

### Core Components

- **ChatService**: Orchestrates chat interactions between agents and sessions
- **AgentManager**: Handles AI model interactions via Strands
- **SessionManager**: Manages conversation persistence
- **Controllers**: Handle HTTP requests and responses

### Adapters

#### Primary Adapters (Inbound)

- `ChatController`: REST API for chat interactions
- `SessionController`: REST API for session management
- `PingController`: Health check endpoint

#### Secondary Adapters (Outbound)

- `StrandsAgentManager`: AWS Bedrock integration via Strands
- `StrandsSessionManager`: File-based session storage

### Ports (Interfaces)

- `AgentManager`: Interface for AI model interactions
- `SessionManager`: Interface for session persistence
- `ChatService`: Interface for chat orchestration

## Dependencies

- **FastAPI**: Web framework
- **Strands**: AI agent framework with AWS Bedrock support
- **Pydantic**: Data validation
- **Structlog**: Structured logging
- **Python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

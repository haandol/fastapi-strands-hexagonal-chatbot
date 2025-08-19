# MCP (Model Context Protocol) Support

This application supports MCP integration through the `StrandsMCPAgentAdapter`, which provides MCP client capabilities while maintaining the hexagonal architecture.

## Architecture

The MCP support is implemented in the secondary adapter layer:

```
ports/
├── chat/
│   └── agent_adapter.py      # Interface with MCP methods
├── mcp/
│   ├── config.py            # MCP configuration models
│   └── __init__.py
└── session/

adapters/secondary/chat/
├── strands_mcp_agent_adapter.py  # MCP-enabled adapter
├── prompt.py
└── __init__.py

utils/
└── mcp.py                   # MCP utility functions
```

## Configuration

### MCP Configuration File

Create `mcp_config.json` in the project root:

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

### Environment-Specific Configuration

You can also create environment-specific configurations:
- `mcp_config/local.json`
- `mcp_config/dev.json`

## Supported Transport Types

### streamable-http
For HTTP-based MCP servers:
```json
{
  "transportType": "streamable-http",
  "url": "https://mcp.example.com/mcp",
  "disabled": false
}
```

### stdio
For command-line MCP servers:
```json
{
  "transportType": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
  "env": {
    "MCP_TRANSPORT": "stdio"
  },
  "disabled": false
}
```

## How It Works

The `StrandsMCPAgentAdapter` automatically:

1. **Loads Configuration**: Reads MCP server configurations from `mcp_config.json`
2. **Initializes Clients**: Creates MCP clients for each enabled server
3. **Connects to Servers**: Establishes connections using the specified transport type
4. **Loads Tools**: Retrieves available tools from connected MCP servers
5. **Creates Agents**: Instantiates agents per session with MCP tools available

## Key Features

### Session-Based Agents
- Each chat session gets its own `Agent` instance
- MCP tools are shared across all sessions
- Agents are cached and reused for the same session

### Resource Management
- Automatic cleanup of MCP clients on shutdown
- Signal handlers for graceful termination (SIGINT, SIGTERM)
- Connection pooling and reuse

### Error Handling
- Failed MCP server connections are logged but don't prevent startup
- Individual tool failures are handled gracefully
- Disabled servers are automatically skipped

## Usage

MCP integration is transparent to the API layer. Once configured, MCP tools are automatically available to the AI agent during chat interactions.

### Example Chat Request
```http
POST /v1/invocations
Content-Type: application/json

{
  "message": "Search for AWS Lambda best practices",
  "session_id": "session_123",
  "stream": false
}
```

The agent will automatically use available MCP tools (like AWS knowledge search) to provide enhanced responses.

## Extensibility

### Adding Custom Tools
The adapter supports adding local tools alongside MCP tools:

```python
# In the adapter
self.local_tools: List[Callable] = []  # Add custom tools here
```

### Adding Hooks
Custom hooks can be added for request/response processing:

```python
# In the adapter  
self.hooks: List[Callable] = []  # Add custom hooks here
```

## Troubleshooting

### Connection Issues
- Check MCP server URLs and availability
- Verify network connectivity for HTTP-based servers
- Ensure command paths are correct for stdio servers

### Configuration Issues
- Validate JSON syntax in configuration files
- Check that required fields are present
- Verify environment variables for stdio servers

### Resource Cleanup
The adapter includes comprehensive cleanup mechanisms:
- Signal handlers for graceful shutdown
- Automatic resource cleanup on exit
- Connection pooling to prevent resource leaks

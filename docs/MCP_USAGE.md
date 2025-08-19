# MCP (Model Context Protocol) Support

This application supports MCP integration through the `StrandsMCPAgentAdapter`, which extends the basic agent functionality with MCP client capabilities while maintaining the hexagonal architecture.

## Architecture

The MCP support is implemented as an alternative adapter that can be swapped in without changing the core business logic:

```
ports/chat/
├── agent_adapter.py          # Interface with MCP methods
├── mcp_config.py            # MCP configuration models
└── dto.py

adapters/secondary/chat/
├── strands_agent_adapter.py     # Basic adapter (no MCP)
└── strands_mcp_agent_adapter.py # MCP-enabled adapter
```

## Configuration

### 1. Create MCP Configuration

Create `mcp_config.json` in the project root:

```json
{
  "mcpServers": {
    "filesystem": {
      "transportType": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    },
    "brave-search": {
      "transportType": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Supported Transport Types

### stdio
For command-line MCP servers:
```json
{
  "transportType": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-name"],
  "env": {
    "MCP_TRANSPORT": "stdio"
  }
}
```

### streamable-http
For HTTP-based MCP servers:
```json
{
  "transportType": "streamable-http",
  "url": "http://localhost:3000/mcp"
}
```

## Usage

When MCP is enabled, the agent will automatically:

1. Load MCP configuration from `mcp_config.json`
2. Initialize MCP clients for each configured server
3. Load available tools from connected servers
4. Make tools available to the AI agent

The MCP tools are seamlessly integrated with the existing chat functionality - no API changes required.

## Extensibility

The architecture allows for easy extension:

### Adding Custom Tools
```python
# In your DI container setup
container = DIContainer(use_mcp=True)
agent_adapter = container.agent_adapter

# Add custom tools
agent_adapter.add_tools([my_custom_tool])

# Add hooks
agent_adapter.add_hooks([my_custom_hook])
```

### Custom MCP Configuration
```python
from ports.chat.mcp_config import MCPConfig

# Create custom config
custom_config = MCPConfig(mcpServers={...})

# Apply to adapter
agent_adapter.configure_mcp(custom_config)
```

## Error Handling

- Failed MCP server connections are logged but don't prevent application startup
- Individual tool failures are handled gracefully
- Disabled servers (with `"disabled": true`) are skipped

## Session Management

Each chat session gets its own agent instance with shared MCP tools, ensuring:
- Session isolation
- Efficient resource usage
- Consistent tool availability across sessions

# Multi-Client Support for Luno MCP Server

This document summarizes the implementation of multi-client support for the Luno MCP Server.

## Implementation Overview

The server now supports two transport mechanisms:

1. **STDIO Transport** - Default single-client mode
2. **WebSockets Transport** - Multi-client support with security features

### Key Components Added

1. **Transport Abstraction Layer**
   - Created a base `MCPTransport` class
   - Implemented `STDIOTransport` for backward compatibility
   - Implemented `WebSocketTransport` for multiple client support

2. **Server Configuration Options**
   - Command-line arguments for transport selection
   - Environment variables for configuration
   - Updated VS Code configuration in `mcp.json`

3. **Security and Rate Limiting Features**
   - SSL/TLS support for secure WebSocket connections (WSS)
   - Rate limiting to prevent abuse (configurable requests per minute)
   - Connection limits to prevent resource exhaustion
   - Maximum message size limits
   - Connection monitoring

4. **Client Tools and Testing**
   - Basic WebSocket test client (`test_websocket_client.py`)
   - Enhanced multi-client simulation tool (`enhanced_websocket_client.py`)
   - Support for connection keep-alive and reconnection

## Usage Instructions

### Starting the Server with WebSockets Support

Basic WebSocket server:
```bash
python -m src.main --transport websocket --host localhost --port 8765
```

With security and rate limiting options:
```bash
python -m src.main --transport websocket --host localhost --port 8765 \
  --max-connections 50 --max-message-size 1048576 --rate-limit 100
```

With SSL/TLS encryption:
```bash
python -m src.main --transport websocket --host localhost --port 8765 \
  --ssl-cert ./certs/server.crt --ssl-key ./certs/server.key
```

### Testing with WebSocket Clients

Basic test client:
```bash
python test_websocket_client.py
```

Enhanced multi-client simulation:
```bash
# Run a single client with monitoring
python enhanced_websocket_client.py --mode single --duration 60

# Run multiple clients to test simultaneous connections
python enhanced_websocket_client.py --mode multi --clients 3 --duration 60
```

## Security Features Implemented

1. **SSL/TLS Encryption**
   - Secure WebSocket connections (WSS) using certificates
   - Configurable certificate and key paths

2. **Rate Limiting**
   - Per-client request rate limiting
   - Configurable limit (default: 100 requests per minute)
   - Automatic tracking and enforcement

3. **Resource Protection**
   - Maximum connection limit (default: 50 clients)
   - Message size limits to prevent memory attacks
   - Queue size controls

4. **Monitoring**
   - Connection monitoring and statistics logging
   - Rate limit status reporting
   - Detailed client connection tracking

## VS Code Integration

The `.vscode/mcp.json` file includes three server configurations:

```json
{
  "servers": {
    "luno-mcp-server-stdio": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.main", "--transport", "stdio"],
      "env": {
        // environment variables
      }
    },
    "luno-mcp-server-websocket": {
      "type": "process",
      "command": "python",
      "args": [
        "-m", "src.main", 
        "--transport", "websocket", 
        // additional parameters
      ],
      "env": {
        // environment variables
      }
    },
    "luno-mcp-server-websocket-secure": {
      "type": "process",
      "command": "python",
      "args": [
        // secure WebSocket parameters
      ],
      "env": {
        // environment variables including SSL paths
      }
    }
  }
}
```

## Next Steps

1. Implement client authentication mechanisms (JWT, API keys, etc.)
2. Add support for SSL client certificates for mutual TLS
3. Consider adding HTTP/REST transport as another option
4. Implement persistent connection state to track sessions
5. Add WebSocket ping/pong frames for better connection health monitoring

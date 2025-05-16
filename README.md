# Luno MCP Server

A Model Context Protocol (MCP) server for the Luno cryptocurrency exchange API. This server provides a standardized interface for AI models and applications to interact with the Luno API for cryptocurrency trading.

<!-- A text-based header instead of potentially broken image link -->
```
 _                        __  __  ____ ____   
| |    _   _ _ __   ___  |  \/  |/ ___|  _ \  
| |   | | | | '_ \ / _ \ | |\/| | |   | |_) | 
| |___| |_| | | | | (_) || |  | | |___|  __/  
|_____|\__,_|_| |_|\___/ |_|  |_|\____|_|     
```

## Features

- Real-time cryptocurrency price information via Luno API
- Market overview for all trading pairs
- Account balance queries
- Order management (place, cancel, status)
- Transaction history retrieval
- Fee information
- Standardized JSON-RPC 2.0 interface
- Simple integration with AI applications

## Prerequisites

- Python 3.8+ (Python 3.9+ recommended)
- `uv` for package management 
- Luno account with API keys (for full functionality)

## Installation

1. Clone this repository
```bash
git clone https://github.com/amanasmuei/mcp-luno.git
cd mcp-luno
```

2. Create a virtual environment using `uv`
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# On Windows use: .venv\Scripts\activate
```

3. Install dependencies
```bash
uv pip install -r requirements.txt
```

4. Configure your Luno API credentials (choose one method):

## Docker Support

You can run the MCP server using Docker for easier deployment and consistent environment across different platforms.

### Using Docker Compose (Recommended)

1. Copy the example environment file and configure your credentials:
```bash
cp .env.example .env
# Edit .env file with your Luno API credentials
```

2. Start the server:
```bash
docker compose up -d
```

The server will be available at `ws://localhost:8765` in WebSocket mode.

3. View logs:
```bash
docker compose logs -f
```

4. Stop the server:
```bash
docker compose down
```

### Using Docker Directly

Build the image:
```bash
docker build -t mcp-luno .
```

Run the container:
```bash
docker run -d \
  -p 8765:8765 \
  -e LUNO_API_KEY=your_api_key_here \
  -e LUNO_API_SECRET=your_api_secret_here \
  -e MCP_TRANSPORT=websocket \
  -e MCP_HOST=0.0.0.0 \
  -v ./certs:/app/certs \
  --name mcp-luno \
  mcp-luno
```

### Using with AI Assistants

After starting the Docker container, you can connect various AI assistants to use the Luno MCP server:

#### Cursor
Add the following to your Cursor configuration:
```json
{
  "mcp_servers": {
    "luno": {
      "type": "websocket",
      "url": "ws://localhost:8765"
    }
  }
}
```

#### Claude Desktop
In Claude Desktop settings, you have two options for configuring the MCP server:

##### Option 1: Using Docker (Recommended)
```json
{
  "mcpServers": {
    "luno": {
      "command": "docker",
      "args": ["compose", "up"],
      "cwd": "/path/to/mcp-luno",
      "transport": "websocket",
      "url": "ws://localhost:8765",
      "env": {
        "LUNO_API_KEY": "your_api_key_here",
        "LUNO_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

This configuration starts the server in a Docker container and connects via WebSocket.

##### Option 2: Using Direct Python Execution
```json
{
  "mcpServers": {
    "luno": {
      "command": "python",
      "args": ["-m", "src.main", "--transport", "stdio"],
      "cwd": "/path/to/mcp-luno",
      "transport": "stdio",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "LUNO_API_KEY": "your_api_key_here",
        "LUNO_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

This configuration runs the Python server directly using STDIO transport.

> Note: Replace `/path/to/mcp-luno` with the actual path where you cloned the repository.

#### Cline
Add the following to your Cline configuration file:
```json
{
  "mcp": {
    "servers": {
      "luno": {
        "transport": "websocket",
        "url": "ws://localhost:8765"
      }
    }
  }
}
```

### SSL Support with Docker

To use SSL with the Docker container:

1. Generate certificates using the provided script:
```bash
./generate_certificates.sh
```

2. Mount the certificates directory when running the container:
```bash
docker run -d \
  -p 8765:8765 \
  -e LUNO_API_KEY=your_api_key_here \
  -e LUNO_API_SECRET=your_api_secret_here \
  -e MCP_TRANSPORT=websocket \
  -e MCP_HOST=0.0.0.0 \
  -v ./certs:/app/certs \
  --name mcp-luno \
  mcp-luno
```

## Manual Installation

   **Option A**: Using `.env` file
   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to add your Luno API credentials:
   ```
   LUNO_API_KEY=your_api_key_here
   LUNO_API_SECRET=your_api_secret_here
   ```

   **Option B**: Using VS Code MCP configuration
   
   Edit the `.vscode/mcp.json` file and add your credentials to the `env` section:
   ```json
   "env": {
     "PYTHONPATH": "${workspaceFolder}",
     "LUNO_API_KEY": "your_api_key_here",
     "LUNO_API_SECRET": "your_api_secret_here",
     "LOG_LEVEL": "INFO"
   }
   ```

> **Note**: Without valid API credentials, only public endpoints will be available.
> **Recommendation**: For security, prefer environment variables when sharing code.

## Running the Server

You can run the MCP server in two different transport modes:

### STDIO Transport (Default, Single Client)

This is the default mode, which supports a single client connection via standard input/output:

```bash
python -m src.main --transport stdio
```

### WebSockets Transport (Multiple Clients)

For supporting multiple client connections simultaneously, run the server in WebSocket mode:

```bash
python -m src.main --transport websocket [--host HOST] [--port PORT]
```

The WebSocket server will start at `ws://localhost:8765` by default.

#### Testing the WebSocket Server

You can test the WebSocket server using the included test client:

```bash
python test_websocket_client.py
```

This helps verify that the server is correctly handling WebSocket connections and responding to requests.

### Command Line Options

- `--transport {stdio,websocket}`: Transport mechanism to use (default: stdio)
- `--host HOST`: Host to bind to when using WebSocket transport (default: localhost)
- `--port PORT`: Port to bind to when using WebSocket transport (default: 8765)

### Environment Variables

You can also configure the transport using environment variables:

- `MCP_TRANSPORT`: Transport mechanism ("stdio" or "websocket")
- `MCP_HOST`: Host to bind to for WebSocket transport
- `MCP_PORT`: Port to bind to for WebSocket transport

### Testing with the Standard Client

For testing the STDIO transport, use the included test client:

```bash
python test_client.py
```

## MCP Protocol Integration

This server implements the Model Context Protocol, which allows AI models to interact with it via standardized JSON-RPC 2.0 messages. The server operates over STDIO by default, making it easy to integrate with VS Code extensions and other MCP-compatible clients.

## VS Code Integration

The `.vscode/mcp.json` file configures the server for use with VS Code. Two server configurations are provided:

1. `luno-mcp-server-stdio` - Uses the STDIO transport (default MCP behavior)
2. `luno-mcp-server-websocket` - Uses the WebSocket transport for multiple client support

### VS Code Configuration

To use the WebSocket transport with VS Code, the `mcp.json` file includes a process-type configuration:

```json
"luno-mcp-server-websocket": {
  "type": "process",
  "command": "python",
  "args": ["-m", "src.main", "--transport", "websocket"],
  "env": {
    // environment variables
  }
}
```

When using the WebSocket transport, VS Code will start the server as a background process rather than communicating via STDIO.

#### Configuring the MCP Server in VS Code

You can configure the server directly from the `.vscode/mcp.json` file:

```json
{
  "servers": {
    "luno-mcp-server": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.main"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "LUNO_API_KEY": "your_api_key_here",
        "LUNO_API_SECRET": "your_api_secret_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

This configuration will be used by VS Code extensions that support the MCP protocol, making it easy to integrate with AI models and other tools.

## Available Methods

| Method | Description | Authentication Required |
|--------|-------------|-------------------------|
| `describe_capabilities` | Return information about server capabilities | No |
| `get_crypto_price` | Get current price for a specific trading pair | No |
| `get_market_overview` | Get an overview of all available markets | No |
| `get_account_balance` | Get the balance of all accounts | Yes |
| `place_order` | Place a new order | Yes |
| `cancel_order` | Cancel an existing order | Yes |
| `get_order_status` | Get the status of an order | Yes |
| `get_transaction_history` | Get transaction history for an account | Yes |
| `get_fees` | Get fee information for a trading pair | Yes |

### Example Requests

Get server capabilities:
```json
{
  "jsonrpc": "2.0",
  "method": "describe_capabilities",
  "params": {},
  "id": 1
}
```

Get Bitcoin-ZAR price:
```json
{
  "jsonrpc": "2.0",
  "method": "get_crypto_price",
  "params": {"pair": "XBTZAR"},
  "id": 2
}
```

## Development

### Project Structure

```text
├── .env                 # Environment variables (API credentials)
├── .gitignore           # Git ignore configuration
├── .vscode/             # VS Code specific settings
│   └── mcp.json         # MCP configuration for VS Code
├── src/                 # Source code
│   ├── main.py          # Entry point
│   └── luno_mcp_server/ # MCP server implementation
│       ├── luno_client.py # Luno API client
│       └── server.py    # MCP server core
├── tests/               # Test suite
├── test_client.py       # Simple test client for the MCP server
├── requirements.txt     # Project dependencies
└── setup.py             # Package setup
```

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Features

To add new Luno API capabilities:

1. Extend the `LunoClient` class in `src/luno_mcp_server/luno_client.py` with new API methods
2. Add corresponding methods in the `LunoMCPServer` class in `src/luno_mcp_server/server.py`
3. Update the `MCP_METHODS` list in `server.py` and register your methods in the `_register_methods` function
4. Add tests in the `tests/` directory

## Architecture

The MCP server uses a simple architecture:
- JSON-RPC 2.0 for communication
- Standard input/output (STDIO) for transport
- Luno API client for cryptocurrency operations

## Troubleshooting

### Common Issues

- **API Authentication Errors**: Ensure your Luno API keys are correctly set in either the `.env` file or in `.vscode/mcp.json`
- **Import Errors**: Make sure you've activated the virtual environment
- **Rate Limiting**: The Luno API has rate limits - implement retry logic for production use

### Configuration Priority

When starting the server, configuration values are loaded in this order of priority:

1. Environment variables passed through MCP configuration (highest priority)
2. Values in the `.env` file 
3. Default values in code (lowest priority)

This means you can set values in the MCP configuration to override any existing values in your `.env` file.

## Multi-Client Support

This MCP server supports multiple client connections simultaneously via WebSockets. For detailed information, see [MULTI_CLIENT_SUPPORT.md](MULTI_CLIENT_SUPPORT.md).

### Transport Options

The server supports two transport mechanisms:

1. **STDIO** (Default): Standard input/output - single client, used by VS Code MCP
2. **WebSockets**: Network transport - multiple clients with security features

### Running with WebSockets Transport

Basic usage:

```bash
python -m src.main --transport websocket --host localhost --port 8765
```

With security options:

```bash
python -m src.main --transport websocket --host localhost --port 8765 \
  --max-connections 50 --max-message-size 1048576 --rate-limit 100
```

With SSL/TLS encryption:

```bash
# First generate certificates
./generate_certificates.sh

# Then run with SSL support
python -m src.main --transport websocket --ssl-cert ./certs/server.crt --ssl-key ./certs/server.key
```

### WebSocket Client Tools

The repository includes two client tools:

1. **test_websocket_client.py**: Simple test client
   ```bash
   python test_websocket_client.py
   ```

2. **enhanced_websocket_client.py**: Advanced client with multi-client simulation
   ```bash
   # Single client mode
   python enhanced_websocket_client.py --mode single
   
   # Multi-client simulation (3 clients)
   python enhanced_websocket_client.py --mode multi --clients 3
   ```
## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.

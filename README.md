# Luno MCP Server

A Model Context Protocol (MCP) server for the Luno cryptocurrency exchange API. This server provides a standardized interface for AI models and applications to interact with the Luno API for cryptocurrency trading.

```
 _                        __  __  ____ ____   
| |    _   _ _ __   ___  |  \/  |/ ___|  _ \  
| |   | | | | '_ \ / _ \ | |\/| | |   | |_) | 
| |___| |_| | | | | (_) || |  | | |___|  __/  
|_____|\__,_|_| |_|\___/ |_|  |_|\____|_|     
```

## Features

- Real-time cryptocurrency price information
- Market overview and account balance queries
- Order management (place, cancel, status)
- Transaction history and fee information
- Multiple transport options (STDIO, WebSocket)
- Docker support with SSL/TLS encryption
- Multi-client support

## Quick Start

### Using Docker (Recommended)

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Luno API credentials
   ```

2. **Start the server:**
   ```bash
   docker compose up -d
   ```

3. **Test connection:**
   ```bash
   python test_client.py
   ```

### Manual Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/amanasmuei/mcp-luno.git
   cd mcp-luno
   uv venv && source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

2. **Configure credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the server:**
   ```bash
   # STDIO mode (single client)
   python -m src.main --transport stdio
   
   # WebSocket mode (multiple clients)
   python -m src.main --transport websocket
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LUNO_API_KEY` | Your Luno API key | Yes* |
| `LUNO_API_SECRET` | Your Luno API secret | Yes* |
| `MCP_TRANSPORT` | Transport type (stdio/websocket) | No |
| `MCP_HOST` | WebSocket host (default: localhost) | No |
| `MCP_PORT` | WebSocket port (default: 8765) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

*Required for authenticated endpoints

### AI Assistant Integration

#### Claude Desktop
```json
{
  "mcpServers": {
    "luno": {
      "command": "docker",
      "args": ["compose", "up"],
      "cwd": "/path/to/mcp-luno",
      "transport": "websocket",
      "url": "ws://localhost:8765"
    }
  }
}
```

#### VS Code / Cursor
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

## API Methods

| Method | Description | Auth Required |
|--------|-------------|---------------|
| `describe_capabilities` | Server capabilities | No |
| `get_crypto_price` | Current price for trading pair | No |
| `get_market_overview` | All market overview | No |
| `get_account_balance` | Account balances | Yes |
| `place_order` | Place new order | Yes |
| `cancel_order` | Cancel existing order | Yes |
| `get_order_status` | Order status | Yes |
| `get_transaction_history` | Transaction history | Yes |
| `get_fees` | Fee information | Yes |

### Example Usage

Get Bitcoin price:
```json
{
  "jsonrpc": "2.0",
  "method": "get_crypto_price",
  "params": {"pair": "XBTZAR"},
  "id": 1
}
```

## Development

### Project Structure
```
├── src/
│   ├── main.py                    # Entry point
│   └── luno_mcp_server/
│       ├── server.py              # MCP server implementation
│       ├── luno_client.py         # Luno API client
│       └── transport.py           # Transport implementations
├── tests/                         # Test suite
├── docker-compose.yml             # Docker configuration
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

### Running Tests
```bash
python -m pytest tests/
```

### Adding Features

1. Extend `LunoClient` in `luno_client.py`
2. Add methods to `LunoMCPServer` in `server.py`
3. Register methods in `_register_methods()`
4. Add tests in `tests/`

## Advanced Features

### Multi-Client Support
See [MULTI_CLIENT_SUPPORT.md](MULTI_CLIENT_SUPPORT.md) for detailed information about WebSocket transport and multiple client connections.

### SSL/TLS Support
```bash
# Generate certificates
./generate_certificates.sh

# Run with SSL
python -m src.main --transport websocket --ssl-cert ./certs/server.crt --ssl-key ./certs/server.key
```

### Docker Options
```bash
# Custom configuration
docker run -d \
  -p 8765:8765 \
  -e LUNO_API_KEY=your_key \
  -e LUNO_API_SECRET=your_secret \
  -e MCP_TRANSPORT=websocket \
  -v ./certs:/app/certs \
  mcp-luno
```

## Troubleshooting

### Common Issues

- **Authentication errors**: Verify API credentials in `.env`
- **Connection refused**: Check if server is running on correct port
- **Rate limiting**: Luno API has rate limits, implement retry logic

### Debug Mode
```bash
LOG_LEVEL=DEBUG python -m src.main
```

## License

MIT License - see LICENSE file for details.

---

**Note**: This MCP server requires valid Luno API credentials for full functionality. Public endpoints (price, market data) work without authentication.

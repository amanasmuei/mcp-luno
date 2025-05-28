# Contributing to Luno MCP Server

## Quick Start for Development

1. **Setup the project:**
   ```bash
   make setup
   # or manually: ./setup.sh
   ```

2. **Test your changes:**
   ```bash
   make test
   make test-ws
   ```

3. **Run the server:**
   ```bash
   make run        # STDIO mode
   make run-ws     # WebSocket mode
   ```

## Project Structure

```
├── src/
│   ├── main.py                    # Entry point
│   └── luno_mcp_server/
│       ├── server.py              # Main MCP server implementation
│       ├── luno_client.py         # Luno API client wrapper
│       └── transport.py           # Transport layer (STDIO/WebSocket)
├── tests/                         # Test suite
├── test_client.py                 # Unified test client
├── docker-compose.yml             # Docker configuration
├── Makefile                       # Development commands
├── setup.sh                       # Setup script
└── README.md                      # Main documentation
```

## Adding New Features

1. **Add Luno API method** in `src/luno_mcp_server/luno_client.py`
2. **Add MCP endpoint** in `src/luno_mcp_server/server.py`:
   - Add method name to `MCP_METHODS` list
   - Add handler to `_setup_methods()`
   - Implement the async method
3. **Add tests** in `tests/`
4. **Update documentation** in `README.md`

## Code Style

- Use type hints for all function parameters and return values
- Follow async/await patterns consistently
- Add docstrings for all public methods
- Use proper error handling with try/except blocks
- Log errors appropriately

## Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific transport
make test       # STDIO
make test-ws    # WebSocket

# Test with Docker
make docker-up
make test-ws
make docker-down
```

## Available Make Commands

Run `make help` to see all available commands:

- `make setup` - Initial project setup
- `make test` - Test STDIO transport
- `make test-ws` - Test WebSocket transport
- `make run` - Run server (STDIO)
- `make run-ws` - Run server (WebSocket)
- `make docker-up` - Start with Docker
- `make docker-down` - Stop Docker containers
- `make clean` - Clean build artifacts

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LUNO_API_KEY` | Luno API key | For private endpoints |
| `LUNO_API_SECRET` | Luno API secret | For private endpoints |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No |
| `MCP_TRANSPORT` | Transport type (stdio/websocket) | No |
| `MCP_HOST` | WebSocket host | No |
| `MCP_PORT` | WebSocket port | No |

## Troubleshooting

- **Import errors**: Ensure virtual environment is activated
- **Connection issues**: Check if server is running on correct port
- **API errors**: Verify Luno credentials in `.env` file
- **Docker issues**: Check `make docker-logs` for container logs

# Luno MCP Server

A Model Context Protocol (MCP) server for the Luno cryptocurrency exchange API. This server provides a standardized interface for AI models and applications to interact with the Luno API for cryptocurrency trading.

![Luno API + MCP](https://www.luno.com/static/images/logos/logo-light.svg)

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
git clone https://github.com/yourusername/mcp-luno.git
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

4. Set up your Luno API credentials
```bash
cp .env.example .env
```

5. Edit the `.env` file to add your Luno API credentials:
```
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here
```

> **Note**: Without valid API credentials, only public endpoints will be available.

## Running the Server

To run the MCP server:

```bash
python -m src.main
```

You can test the server using the included test client:

```bash
python test_client.py
```

## MCP Protocol Integration

This server implements the Model Context Protocol, which allows AI models to interact with it via standardized JSON-RPC 2.0 messages. The server operates over STDIO by default, making it easy to integrate with VS Code extensions and other MCP-compatible clients.

### VS Code Integration

The `.vscode/mcp.json` file configures the server for use with VS Code. The server can be automatically discovered by MCP-compatible extensions.

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

```
├── .env                 # Environment variables (API credentials)
├── .vscode/             # VS Code specific settings
│   └── mcp.json         # MCP configuration for VS Code
├── src/                 # Source code
│   ├── main.py          # Entry point
│   └── luno_mcp_server/ # MCP server implementation
│       ├── luno_client.py # Luno API client
│       └── server.py    # MCP server core
├── tests/               # Test suite
├── requirements.txt     # Project dependencies
└── setup.py            # Package setup
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

- **API Authentication Errors**: Ensure your Luno API keys are correctly set in the `.env` file
- **Import Errors**: Make sure you've activated the virtual environment
- **Rate Limiting**: The Luno API has rate limits - implement retry logic for production use

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.

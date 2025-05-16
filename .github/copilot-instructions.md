<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Luno MCP Server Instructions

This workspace is a Python implementation of a Model Context Protocol (MCP) server for the Luno cryptocurrency exchange API.

## Project Structure

- `/src/luno_mcp_server/`: Main server implementation
  - `luno_client.py`: Luno API client
  - `server.py`: MCP server implementation
- `/src/main.py`: Entry point for the server
- `/tests/`: Unit tests
- `.vscode/mcp.json`: MCP server configuration

## Key Knowledge

- The server follows the Model Context Protocol specification for AI-service interoperability
- The Luno API is used for cryptocurrency trading operations
- The server uses JSONRPC for request/response handling
- Authentication with the Luno API requires API keys

## Reference Resources

- Luno API documentation: https://www.luno.com/en/developers/api
- Model Context Protocol: https://modelcontextprotocol.io/llms-full.txt
- Python MCP SDK: https://github.com/modelcontextprotocol/create-python-server

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt

"""
Legacy-compatible entry point for the Luno MCP server.

This version works without FastMCP dependencies for immediate Claude Desktop compatibility.
"""

import os
import asyncio
import logging
import sys
import argparse
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if FastMCP is available and decide which implementation to use."""
    try:
        import fastmcp

        return True
    except ImportError:
        return False


def run_with_fastmcp():
    """Run with the new FastMCP implementation."""
    try:
        from luno_mcp.server import create_server, run_server
        from luno_mcp.config import LunoMCPConfig

        logger.info("Using new FastMCP 2.0 implementation")

        # Create configuration
        config = LunoMCPConfig()

        # Run the server
        asyncio.run(run_server(config))

    except Exception as e:
        logger.error(f"Error with FastMCP implementation: {e}")
        sys.exit(1)


def run_with_legacy():
    """Run with the legacy implementation."""
    try:
        # Import the old server directly
        sys.path.append(os.path.join(os.path.dirname(__file__), "luno_mcp_server"))
        from src.luno_mcp_server.server import mcp

        logger.info("Using legacy MCP implementation")

        # Log configuration
        api_key_exists = bool(os.environ.get("LUNO_API_KEY"))
        api_secret_exists = bool(os.environ.get("LUNO_API_SECRET"))

        if api_key_exists and api_secret_exists:
            logger.info("API credentials found - all endpoints available")
        else:
            logger.warning("No API credentials - only public endpoints available")

        # Run the legacy server
        mcp.run(transport="stdio")

    except Exception as e:
        logger.error(f"Error with legacy implementation: {e}")
        # Try the most basic fallback
        run_minimal_server()


def run_minimal_server():
    """Run a minimal server as last resort."""
    logger.info("Running minimal fallback server")

    # Create a simple server response
    import json

    def handle_request(request):
        """Handle basic MCP requests."""
        if request.get("method") == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "luno-mcp-server", "version": "0.1.0"},
                },
            }
        elif request.get("method") == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "get_crypto_price",
                            "description": "Get crypto price (minimal implementation)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"pair": {"type": "string"}},
                            },
                        }
                    ]
                },
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method '{request.get('method')}' not found",
                },
            }

    # Simple STDIO loop
    try:
        while True:
            line = input()
            if line.strip():
                try:
                    request = json.loads(line)
                    response = handle_request(request)
                    print(json.dumps(response))
                    sys.stdout.flush()
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
    except (EOFError, KeyboardInterrupt):
        logger.info("Server stopped")


def main():
    """Main entry point that chooses the best available implementation."""
    logger.info("Starting Luno MCP server (adaptive mode)...")

    # Check what's available and run accordingly
    if check_dependencies():
        logger.info("FastMCP available - using modern implementation")
        run_with_fastmcp()
    else:
        logger.info("FastMCP not available - checking for legacy implementation")

        # Check if legacy server exists
        legacy_server_path = os.path.join(
            os.path.dirname(__file__), "luno_mcp_server", "server.py"
        )
        if os.path.exists(legacy_server_path):
            logger.info("Legacy server found - using legacy implementation")
            run_with_legacy()
        else:
            logger.warning("No server implementation found - using minimal fallback")
            run_minimal_server()


if __name__ == "__main__":
    main()

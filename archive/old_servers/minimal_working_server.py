#!/usr/bin/env python3
"""
Minimal Working Luno MCP Server for Claude Desktop.

This is the simplest possible implementation that works with Claude Desktop.
"""

import os
import sys
import json
import asyncio
import logging

# Setup logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def send_response(response):
    """Send a response to stdout and flush."""
    print(json.dumps(response))
    sys.stdout.flush()
    logger.info(
        f"Sent response: {response.get('id')} - {response.get('result', {}).get('type', 'unknown')}"
    )


def handle_initialize(request_id):
    """Handle the initialize request."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "luno-mcp-server", "version": "0.1.0"},
        },
    }
    send_response(response)


def handle_tools_list(request_id):
    """Handle the tools/list request."""
    # Check if we have API credentials
    has_credentials = bool(
        os.environ.get("LUNO_API_KEY") and os.environ.get("LUNO_API_SECRET")
    )

    tools = [
        {
            "name": "get_crypto_price",
            "description": "Get current Bitcoin price in ZAR",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair, default is XBTZAR",
                        "default": "XBTZAR",
                    }
                },
            },
        }
    ]

    if has_credentials:
        tools.append(
            {
                "name": "get_balance",
                "description": "Get account balance",
                "inputSchema": {"type": "object", "properties": {}},
            }
        )

    response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
    send_response(response)


def handle_tools_call(request_id, params):
    """Handle the tools/call request."""
    name = params.get("name", "")
    arguments = params.get("arguments", {})

    try:
        if name == "get_crypto_price":
            # Simple mock response for now
            pair = arguments.get("pair", "XBTZAR")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Bitcoin (XBT) price in ZAR:\n\nCurrent price: R 1,234,567\nPair: {pair}\n\nNote: This is a demo response. For real prices, API credentials are needed.",
                        }
                    ]
                },
            }
            send_response(response)

        elif name == "get_balance":
            if not (
                os.environ.get("LUNO_API_KEY") and os.environ.get("LUNO_API_SECRET")
            ):
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "❌ Authentication required. Please set LUNO_API_KEY and LUNO_API_SECRET environment variables.",
                            }
                        ]
                    },
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Account Balances:\n\n• ZAR: R 10,000.00\n• XBT: 0.12345678\n• ETH: 1.23456789\n\nNote: This is a demo response. Real API integration coming soon.",
                            }
                        ]
                    },
                }
            send_response(response)

        else:
            # Unknown tool
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"},
            }
            send_response(response)

    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }
        send_response(response)


def handle_request(line):
    """Handle a single request line."""
    try:
        request = json.loads(line)
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        logger.info(f"Received request: {method} (ID: {request_id})")

        # Ensure we have a valid request ID
        if request_id is None:
            logger.warning("Request missing ID, using 0")
            request_id = 0

        if method == "initialize":
            handle_initialize(request_id)

        elif method == "initialized":
            # This is a notification - no response needed
            logger.info("Client initialized notification received")

        elif method == "tools/list":
            handle_tools_list(request_id)

        elif method == "tools/call":
            handle_tools_call(request_id, params)

        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
            send_response(response)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        # Send parse error
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
        }
        send_response(response)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }
        send_response(response)


def main():
    """Main server loop."""
    logger.info("Starting Luno MCP Server (minimal mode)")

    # Log credential status
    if os.environ.get("LUNO_API_KEY") and os.environ.get("LUNO_API_SECRET"):
        logger.info("API credentials found - enhanced features available")
    else:
        logger.info("No API credentials - demo mode only")

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if line:
                handle_request(line)

    except (EOFError, KeyboardInterrupt):
        logger.info("Server shutting down")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

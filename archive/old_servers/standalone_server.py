#!/usr/bin/env python3
"""
Standalone Luno MCP Server - No external dependencies required.

This is a self-contained MCP server that works with Claude Desktop without
requiring FastMCP or other external libraries.
"""

import os
import sys
import json
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class LunoClient:
    """Simple Luno API client without external dependencies."""

    BASE_URL = "https://api.luno.com"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret

    async def _request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the Luno API."""
        import httpx

        auth = None
        if self.api_key and self.api_secret:
            auth = (self.api_key, self.api_secret)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.BASE_URL}{endpoint}",
                params=params,
                auth=auth,
            )
            response.raise_for_status()
            return response.json()

    async def get_ticker(self, pair: str) -> Dict[str, Any]:
        """Get ticker for a currency pair."""
        return await self._request("GET", "/api/1/ticker", {"pair": pair})

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary."""
        return await self._request("GET", "/api/exchange/1/markets")

    async def get_balances(self) -> Dict[str, Any]:
        """Get account balances."""
        return await self._request("GET", "/api/1/balance")


class StandaloneMCPServer:
    """Standalone MCP server implementation."""

    def __init__(self):
        self.client = LunoClient(
            api_key=os.environ.get("LUNO_API_KEY"),
            api_secret=os.environ.get("LUNO_API_SECRET"),
        )

        # Log credentials status
        if self.client.api_key and self.client.api_secret:
            logger.info("API credentials loaded - all endpoints available")
        else:
            logger.warning("No API credentials - only public endpoints available")

    def get_server_info(self) -> Dict[str, Any]:
        """Get server info for initialization."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "luno-mcp-server", "version": "0.1.0"},
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        tools = [
            {
                "name": "get_crypto_price",
                "description": "Get current price for a cryptocurrency trading pair",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pair": {
                            "type": "string",
                            "description": "Trading pair (e.g., 'XBTZAR', 'ETHZAR')",
                        }
                    },
                    "required": ["pair"],
                },
            },
            {
                "name": "get_market_overview",
                "description": "Get overview of all available markets",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

        # Add private tools if authenticated
        if self.client.api_key and self.client.api_secret:
            tools.append(
                {
                    "name": "get_account_balance",
                    "description": "Get account balances for all currencies",
                    "inputSchema": {"type": "object", "properties": {}},
                }
            )

        return tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool and return the result."""
        try:
            if name == "get_crypto_price":
                pair = arguments.get("pair", "")
                ticker = await self.client.get_ticker(pair)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "pair": pair,
                                    "ask": ticker.get("ask"),
                                    "bid": ticker.get("bid"),
                                    "last_trade": ticker.get("last_trade"),
                                    "timestamp": ticker.get("timestamp"),
                                    "status": "success",
                                },
                                indent=2,
                            ),
                        }
                    ]
                }

            elif name == "get_market_overview":
                markets = await self.client.get_market_summary()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"markets": markets, "status": "success"}, indent=2
                            ),
                        }
                    ]
                }

            elif name == "get_account_balance":
                if not (self.client.api_key and self.client.api_secret):
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    {
                                        "error": "Authentication required. Please set LUNO_API_KEY and LUNO_API_SECRET.",
                                        "status": "error",
                                    },
                                    indent=2,
                                ),
                            }
                        ]
                    }

                balances = await self.client.get_balances()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"balances": balances, "status": "success"}, indent=2
                            ),
                        }
                    ]
                }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"error": f"Unknown tool: {name}", "status": "error"},
                                indent=2,
                            ),
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"error": str(e), "status": "error"}, indent=2
                        ),
                    }
                ]
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests."""
        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self.get_server_info(),
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.list_tools()},
            }

        elif method == "tools/call":
            # This will be handled async
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

    async def handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        request_id = request.get("id")

        result = await self.call_tool(name, arguments)

        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    async def run(self):
        """Run the server using STDIO transport."""
        logger.info("Starting Luno MCP Server (standalone mode)")

        try:
            while True:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    logger.info(f"Received request: {request.get('method')}")

                    # Handle different request types
                    if request.get("method") == "tools/call":
                        response = await self.handle_tool_call(request)
                    else:
                        response = self.handle_request(request)

                    if response:
                        print(json.dumps(response))
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                except Exception as e:
                    logger.error(f"Error handling request: {e}")

        except (EOFError, KeyboardInterrupt):
            logger.info("Server stopped")


async def main():
    """Main entry point."""
    server = StandaloneMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

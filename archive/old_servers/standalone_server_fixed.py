#!/usr/bin/env python3
"""
Fixed Standalone Luno MCP Server - Proper MCP protocol implementation.

This server correctly implements the Model Context Protocol for Claude Desktop.
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
    """Simple Luno API client."""

    BASE_URL = "https://api.luno.com"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret

    async def _request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the Luno API."""
        auth = None
        if self.api_key and self.api_secret:
            auth = (self.api_key, self.api_secret)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.BASE_URL}{endpoint}",
                params=params,
                auth=auth,
                timeout=10.0,
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
    """Standalone MCP server implementation with proper protocol handling."""

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

    def create_response(
        self, request_id: Any, result: Any = None, error: Any = None
    ) -> Dict[str, Any]:
        """Create a proper JSON-RPC response."""
        response = {"jsonrpc": "2.0", "id": request_id}

        if error:
            response["error"] = error
        else:
            response["result"] = result

        return response

    def create_error(self, code: int, message: str) -> Dict[str, Any]:
        """Create a proper JSON-RPC error."""
        return {"code": code, "message": message}

    def handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialize request."""
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "luno-mcp-server", "version": "0.1.0"},
        }
        return self.create_response(request_id, result)

    def handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
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

        return self.create_response(request_id, {"tools": tools})

    async def handle_tools_call(
        self, request_id: Any, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle tools/call request."""
        try:
            name = params.get("name")
            arguments = params.get("arguments", {})

            if name == "get_crypto_price":
                pair = arguments.get("pair", "")
                if not pair:
                    return self.create_response(
                        request_id,
                        error=self.create_error(
                            -32602, "Missing required parameter: pair"
                        ),
                    )

                ticker = await self.client.get_ticker(pair)
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Current price for {pair}:\n"
                            f"Ask: {ticker.get('ask', 'N/A')}\n"
                            f"Bid: {ticker.get('bid', 'N/A')}\n"
                            f"Last Trade: {ticker.get('last_trade', 'N/A')}\n"
                            f"Volume (24h): {ticker.get('rolling_24_hour_volume', 'N/A')}",
                        }
                    ]
                }
                return self.create_response(request_id, result)

            elif name == "get_market_overview":
                markets = await self.client.get_market_summary()
                market_list = markets.get("markets", [])

                if isinstance(market_list, list):
                    market_text = f"Available markets ({len(market_list)} total):\n"
                    for market in market_list[:10]:  # Show first 10
                        market_text += f"- {market.get('market_id', 'Unknown')}: {market.get('trading_status', 'Unknown')}\n"
                    if len(market_list) > 10:
                        market_text += f"... and {len(market_list) - 10} more markets"
                else:
                    market_text = f"Markets data: {json.dumps(markets, indent=2)}"

                result = {"content": [{"type": "text", "text": market_text}]}
                return self.create_response(request_id, result)

            elif name == "get_account_balance":
                if not (self.client.api_key and self.client.api_secret):
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": "❌ Authentication required. Please set LUNO_API_KEY and LUNO_API_SECRET environment variables.",
                            }
                        ]
                    }
                    return self.create_response(request_id, result)

                balances = await self.client.get_balances()
                balance_list = balances.get("balance", [])

                if isinstance(balance_list, list):
                    balance_text = "Account Balances:\n"
                    for balance in balance_list:
                        asset = balance.get("asset", "Unknown")
                        available = balance.get("balance", "0")
                        reserved = balance.get("reserved", "0")
                        balance_text += (
                            f"- {asset}: {available} (Reserved: {reserved})\n"
                        )
                else:
                    balance_text = f"Balance data: {json.dumps(balances, indent=2)}"

                result = {"content": [{"type": "text", "text": balance_text}]}
                return self.create_response(request_id, result)

            else:
                return self.create_response(
                    request_id, error=self.create_error(-32601, f"Unknown tool: {name}")
                )

        except Exception as e:
            logger.error(f"Error calling tool {params.get('name')}: {e}")
            return self.create_response(
                request_id, error=self.create_error(-32603, f"Internal error: {str(e)}")
            )

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        logger.info(f"Handling request: {method}")

        try:
            if method == "initialize":
                return self.handle_initialize(request_id)

            elif method == "initialized":
                # This is a notification, no response needed
                logger.info("Client initialized successfully")
                return None

            elif method == "tools/list":
                return self.handle_tools_list(request_id)

            elif method == "tools/call":
                return await self.handle_tools_call(request_id, params)

            else:
                return self.create_response(
                    request_id,
                    error=self.create_error(-32601, f"Method not found: {method}"),
                )

        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return self.create_response(
                request_id, error=self.create_error(-32603, f"Internal error: {str(e)}")
            )

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
                    response = await self.handle_request(request)

                    if response:
                        print(json.dumps(response))
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    # Send error response if we can extract an ID
                    try:
                        partial = json.loads(line[: line.find("}") + 1])
                        error_response = self.create_response(
                            partial.get("id"),
                            error=self.create_error(-32700, "Parse error"),
                        )
                        print(json.dumps(error_response))
                        sys.stdout.flush()
                    except:
                        pass

                except Exception as e:
                    logger.error(f"Error processing request: {e}")

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

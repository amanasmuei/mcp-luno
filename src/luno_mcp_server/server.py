"""
MCP Server implementation for the Luno API.
This module implements the Model Context Protocol for interacting with the Luno cryptocurrency exchange API.
"""

import sys
import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional

from .luno_client import LunoClient
from .transport import MCPTransport, STDIOTransport, WebSocketTransport

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Available MCP methods
MCP_METHODS = [
    "get_crypto_price",
    "get_market_overview",
    "get_account_balance",
    "place_order",
    "cancel_order",
    "get_order_status",
    "get_transaction_history",
    "get_fees",
]


class LunoMCPServer:
    """MCP server for the Luno cryptocurrency exchange API."""

    def __init__(self):
        """Initialize the MCP server."""
        self.client = None
        self.methods = self._setup_methods()

    def _setup_methods(self) -> Dict[str, callable]:
        """Setup method handlers."""
        return {
            "describe_capabilities": self.describe_capabilities,
            "get_crypto_price": self.get_crypto_price,
            "get_market_overview": self.get_market_overview,
            "get_account_balance": self.get_account_balance,
            "place_order": self.place_order,
            "cancel_order": self.cancel_order,
            "get_order_status": self.get_order_status,
            "get_transaction_history": self.get_transaction_history,
            "get_fees": self.get_fees,
        }

    async def initialize_client(self) -> LunoClient:
        """Initialize the Luno API client."""
        if self.client is None:
            api_key = os.environ.get("LUNO_API_KEY")
            api_secret = os.environ.get("LUNO_API_SECRET")

            # Configure logging
            log_level = os.environ.get("LOG_LEVEL", "INFO")
            logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))

            self.client = LunoClient(api_key=api_key, api_secret=api_secret)

            if api_key and api_secret:
                logger.info("API credentials loaded from environment")
            else:
                logger.warning(
                    "No API credentials found - only public endpoints available"
                )

        return self.client

    # Server capabilities
    async def describe_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities."""
        return {
            "name": "luno_mcp_server",
            "version": "0.1.0",
            "description": "MCP server for Luno cryptocurrency exchange API",
            "vendor": {
                "name": "Luno API MCP Server",
                "url": "https://www.luno.com/en/developers/api",
            },
            "methods": MCP_METHODS,
            "capabilities": {
                "authentication": ["api_key"],
                "rate_limiting": True,
                "streaming": False,
            },
        }

    # Public endpoints (no auth required)
    async def get_crypto_price(self, pair: str) -> Dict[str, Any]:
        """Get current price for a trading pair."""
        client = await self.initialize_client()
        try:
            ticker = await client.get_ticker(pair)
            return {
                "pair": pair,
                "ask": ticker.get("ask"),
                "bid": ticker.get("bid"),
                "last_trade": ticker.get("last_trade"),
                "rolling_24_hour_volume": ticker.get("rolling_24_hour_volume"),
                "timestamp": ticker.get("timestamp"),
            }
        except Exception as e:
            logger.error(f"Error getting price for {pair}: {e}")
            return {"error": str(e), "pair": pair}

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get overview of all available markets."""
        client = await self.initialize_client()
        try:
            markets = await client.get_market_summary()
            return {"markets": markets}
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {"error": str(e)}

    # Private endpoints (auth required)
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balances."""
        client = await self.initialize_client()
        try:
            return await client.get_balances()
        except Exception as e:
            logger.error(f"Error getting account balances: {e}")
            return {"error": str(e)}

    async def place_order(
        self,
        type: str,
        pair: str,
        price: Optional[str] = None,
        volume: Optional[str] = None,
        base_account_id: Optional[str] = None,
        counter_account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Place a new order."""
        client = await self.initialize_client()
        try:
            return await client.create_order(
                type=type,
                pair=pair,
                price=price,
                volume=volume,
                base_amount=base_account_id,
                counter_amount=counter_account_id,
            )
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"error": str(e)}

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        client = await self.initialize_client()
        try:
            return await client.stop_order(order_id)
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            return {"error": str(e), "order_id": order_id}

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        client = await self.initialize_client()
        try:
            return await client.get_order(order_id)
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return {"error": str(e), "order_id": order_id}

    async def get_transaction_history(
        self,
        account_id: str,
        min_row: Optional[int] = None,
        max_row: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get transaction history for an account."""
        client = await self.initialize_client()
        try:
            return await client.get_transactions(account_id, min_row, max_row)
        except Exception as e:
            logger.error(f"Error getting transaction history for {account_id}: {e}")
            return {"error": str(e), "account_id": account_id}

    async def get_fees(self, pair: str) -> Dict[str, Any]:
        """Get fee information for a trading pair."""
        client = await self.initialize_client()
        try:
            return await client.get_fee_info(pair)
        except Exception as e:
            logger.error(f"Error getting fees for {pair}: {e}")
            return {"error": str(e), "pair": pair}

    # Request handling
    async def handle_request(self, request_json: str) -> str:
        """Handle incoming MCP request."""
        try:
            request = json.loads(request_json)
            logger.info(f"Received request: {request}")

            method = request.get("method")
            if not method:
                return self._error_response("No method specified", request.get("id"))

            params = request.get("params", {})
            handler = self.methods.get(method)

            if not handler:
                return self._error_response(
                    f"Method '{method}' not found", request.get("id"), code=-32601
                )

            result = await handler(**params)
            return json.dumps(
                {"jsonrpc": "2.0", "result": result, "id": request.get("id")}
            )

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {request_json}")
            return self._error_response("Invalid JSON", None)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._error_response(str(e), None)

    def _error_response(self, message: str, request_id: Any, code: int = -32603) -> str:
        """Generate error response."""
        error = {"code": code, "message": message} if code != -32603 else message
        return json.dumps({"jsonrpc": "2.0", "error": error, "id": request_id})

    # Transport methods
    async def run_with_transport(self, transport: MCPTransport):
        """Run server with specified transport."""
        await self.initialize_client()
        logger.info(f"Luno MCP Server started with {transport.__class__.__name__}")

        try:
            await transport.run(self.handle_request)
        except Exception as e:
            logger.error(f"Transport error: {e}")
        finally:
            if self.client:
                await self.client.close()
            logger.info("Luno MCP Server shutting down")

    async def run(
        self,
        transport_type: str = "stdio",
        host: str = "localhost",
        port: int = 8765,
        **kwargs,
    ):
        """Run the server."""
        if transport_type.lower() == "websocket":
            transport = WebSocketTransport(host=host, port=port, **kwargs)
        else:
            transport = STDIOTransport()

        await self.run_with_transport(transport)

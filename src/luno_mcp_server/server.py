"""
MCP Server implementation for the Luno API.
This module implements the Model Context Protocol for interacting with the Luno cryptocurrency exchange API.
"""

import sys
import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from .luno_client import LunoClient


# Simple dispatcher to map method names to handler functions
class SimpleDispatcher:
    def __init__(self):
        self.methods = {}


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Define MCP methods
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
    """
    Model Context Protocol (MCP) server for the Luno cryptocurrency exchange API.

    This server implements the MCP protocol to provide a standardized interface
    for AI models to interact with the Luno API for cryptocurrency trading.
    """

    def __init__(self):
        """Initialize the MCP server with a Luno API client."""
        self.dispatcher = SimpleDispatcher()
        self.client = None
        self._register_methods()

    def _register_methods(self):
        """Register all available methods with the dispatcher."""
        self.dispatcher.methods["get_crypto_price"] = self.get_crypto_price
        self.dispatcher.methods["get_market_overview"] = self.get_market_overview
        self.dispatcher.methods["get_account_balance"] = self.get_account_balance
        self.dispatcher.methods["place_order"] = self.place_order
        self.dispatcher.methods["cancel_order"] = self.cancel_order
        self.dispatcher.methods["get_order_status"] = self.get_order_status
        self.dispatcher.methods["get_transaction_history"] = (
            self.get_transaction_history
        )
        self.dispatcher.methods["get_fees"] = self.get_fees
        self.dispatcher.methods["describe_capabilities"] = self.describe_capabilities

    async def initialize_client(self):
        """Initialize the Luno API client with configuration from environment."""
        if self.client is None:
            # Get configuration from environment variables
            api_key = os.environ.get("LUNO_API_KEY")
            api_secret = os.environ.get("LUNO_API_SECRET")

            # Configure logging level if specified
            log_level = os.environ.get("LOG_LEVEL", "INFO")
            logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))

            # Initialize client with environment-provided credentials
            self.client = LunoClient(api_key=api_key, api_secret=api_secret)

            # Log configuration source
            if api_key and api_secret:
                logger.info("Using API credentials from environment configuration")
            else:
                logger.warning("No API credentials found in environment configuration")

        return self.client

    async def describe_capabilities(self) -> Dict[str, Any]:
        """
        Return information about the server's capabilities.

        This method is required by the MCP protocol and is used to inform
        the client about available methods and their parameters.
        """
        return {
            "name": "luno_mcp_server",
            "version": "0.1.0",
            "description": "Model Context Protocol server for the Luno cryptocurrency exchange API",
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

    async def get_crypto_price(self, pair: str) -> Dict[str, Any]:
        """
        Get the current price of a cryptocurrency pair.

        Args:
            pair: The trading pair to get the price for (e.g., "XBTZAR" for Bitcoin-ZAR)

        Returns:
            A dictionary with price information
        """
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
            logger.error(f"Error getting price for {pair}: {str(e)}")
            return {"error": str(e), "pair": pair}

    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Get an overview of all available markets and their current status.

        Returns:
            A dictionary with market information
        """
        client = await self.initialize_client()
        try:
            markets = await client.get_market_summary()
            return {"markets": markets}
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return {"error": str(e)}

    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Get the balance of all accounts.

        Returns:
            A dictionary with account balance information
        """
        client = await self.initialize_client()
        try:
            balances = await client.get_balances()
            return balances
        except Exception as e:
            logger.error(f"Error getting account balances: {str(e)}")
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
        """
        Place a new order.

        Args:
            type: Order type (BID or ASK)
            pair: Trading pair
            price: Limit price
            volume: Amount to trade
            base_account_id: Account ID to use for base currency
            counter_account_id: Account ID to use for counter currency

        Returns:
            A dictionary with order information
        """
        client = await self.initialize_client()
        try:
            order = await client.create_order(
                type=type,
                pair=pair,
                price=price,
                volume=volume,
                base_amount=base_account_id,
                counter_amount=counter_account_id,
            )
            return order
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {"error": str(e)}

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            order_id: ID of the order to cancel

        Returns:
            A dictionary with the cancellation result
        """
        client = await self.initialize_client()
        try:
            result = await client.stop_order(order_id)
            return result
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            return {"error": str(e), "order_id": order_id}

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an order.

        Args:
            order_id: ID of the order

        Returns:
            A dictionary with order status information
        """
        client = await self.initialize_client()
        try:
            order = await client.get_order(order_id)
            return order
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {str(e)}")
            return {"error": str(e), "order_id": order_id}

    async def get_transaction_history(
        self,
        account_id: str,
        min_row: Optional[int] = None,
        max_row: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get transaction history for an account.

        Args:
            account_id: ID of the account
            min_row: Minimum row to return (pagination)
            max_row: Maximum row to return (pagination)

        Returns:
            A dictionary with transaction information
        """
        client = await self.initialize_client()
        try:
            transactions = await client.get_transactions(account_id, min_row, max_row)
            return transactions
        except Exception as e:
            logger.error(
                f"Error getting transaction history for {account_id}: {str(e)}"
            )
            return {"error": str(e), "account_id": account_id}

    async def get_fees(self, pair: str) -> Dict[str, Any]:
        """
        Get fee information for a currency pair.

        Args:
            pair: Trading pair

        Returns:
            A dictionary with fee information
        """
        client = await self.initialize_client()
        try:
            fees = await client.get_fee_info(pair)
            return fees
        except Exception as e:
            logger.error(f"Error getting fees for {pair}: {str(e)}")
            return {"error": str(e), "pair": pair}

    async def handle_request(self, request_json: str) -> str:
        """
        Handle an incoming MCP request.

        Args:
            request_json: The JSON-RPC request as a string

        Returns:
            The JSON-RPC response as a string
        """
        try:
            # Parse the request
            request = json.loads(request_json)
            logger.info(f"Received request: {request}")

            # Get the method name
            method = request.get("method")
            if not method:
                logger.error("No method specified in request")
                return json.dumps(
                    {"error": "No method specified", "id": request.get("id")}
                )

            # Get the parameters
            params = request.get("params", {})

            # Get the handler for the method
            handler = self.dispatcher.methods.get(method)
            if not handler:
                logger.error(f"Unknown method: {method}")
                return json.dumps(
                    {
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found",
                        },
                        "id": request.get("id"),
                    }
                )

            # Call the handler
            result = await handler(**params)

            # Return the result
            response = {"jsonrpc": "2.0", "result": result, "id": request.get("id")}

            return json.dumps(response)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {request_json}")
            return json.dumps({"error": "Invalid JSON", "id": None})
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return json.dumps({"error": str(e), "id": None})

    async def run_forever(self):
        """
        Run the server indefinitely, reading from stdin and writing to stdout.

        This is the main entry point for the MCP server when run as a stdio process.
        """
        await self.initialize_client()

        logger.info("LunoMCPServer started. Reading from stdin...")

        while True:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break

            # Strip newline
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Handle the request
            response = await self.handle_request(line)

            # Write the response to stdout
            print(response, flush=True)

        logger.info("LunoMCPServer shutting down...")
        await self.client.close()

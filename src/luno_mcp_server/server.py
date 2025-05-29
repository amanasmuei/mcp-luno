"""
MCP Server implementation for the Luno API using FastMCP framework.
This module implements the Model Context Protocol for interacting with the Luno cryptocurrency exchange API.
"""

import os
import logging
from typing import Dict, Any, Optional

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastmcp import FastMCP
from luno_mcp_server.luno_client import LunoClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name="luno_mcp_server",
    description="MCP server for Luno cryptocurrency exchange API",
)

# Global client instance
client: Optional[LunoClient] = None


async def get_client() -> LunoClient:
    """Get or initialize the Luno API client."""
    global client
    if client is None:
        api_key = os.environ.get("LUNO_API_KEY")
        api_secret = os.environ.get("LUNO_API_SECRET")

        # Configure logging
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))

        client = LunoClient(api_key=api_key, api_secret=api_secret)

        if api_key and api_secret:
            logger.info("API credentials loaded from environment")
        else:
            logger.warning("No API credentials found - only public endpoints available")

    return client


# Public endpoints (no auth required)
@mcp.tool()
async def get_crypto_price(pair: str) -> Dict[str, Any]:
    """Get current price for a trading pair.

    Args:
        pair: Trading pair (e.g., 'XBTZAR', 'ETHZAR')

    Returns:
        Dictionary containing price information including ask, bid, last_trade, etc.
    """
    client = await get_client()
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


@mcp.tool()
async def get_market_overview() -> Dict[str, Any]:
    """Get overview of all available markets.

    Returns:
        Dictionary containing information about all available trading markets.
    """
    client = await get_client()
    try:
        markets = await client.get_market_summary()
        return {"markets": markets}
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return {"error": str(e)}


# Private endpoints (auth required)
@mcp.tool()
async def get_account_balance() -> Dict[str, Any]:
    """Get account balances.

    Returns:
        Dictionary containing account balance information for all currencies.
    """
    client = await get_client()
    try:
        return await client.get_balances()
    except Exception as e:
        logger.error(f"Error getting account balances: {e}")
        return {"error": str(e)}


@mcp.tool()
async def place_order(
    type: str,
    pair: str,
    price: Optional[str] = None,
    volume: Optional[str] = None,
    base_account_id: Optional[str] = None,
    counter_account_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Place a new order.

    Args:
        type: Order type ('BID' for buy, 'ASK' for sell)
        pair: Trading pair (e.g., 'XBTZAR', 'ETHZAR')
        price: Price per unit (optional for market orders)
        volume: Amount to trade (optional, use base_account_id for market orders)
        base_account_id: Account ID for base currency (optional)
        counter_account_id: Account ID for counter currency (optional)

    Returns:
        Dictionary containing order information including order_id.
    """
    client = await get_client()
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


@mcp.tool()
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an existing order.

    Args:
        order_id: ID of the order to cancel

    Returns:
        Dictionary containing cancellation status information.
    """
    client = await get_client()
    try:
        return await client.stop_order(order_id)
    except Exception as e:
        logger.error(f"Error canceling order {order_id}: {e}")
        return {"error": str(e), "order_id": order_id}


@mcp.tool()
async def get_order_status(order_id: str) -> Dict[str, Any]:
    """Get order status.

    Args:
        order_id: ID of the order to check

    Returns:
        Dictionary containing detailed order information and status.
    """
    client = await get_client()
    try:
        return await client.get_order(order_id)
    except Exception as e:
        logger.error(f"Error getting order status for {order_id}: {e}")
        return {"error": str(e), "order_id": order_id}


@mcp.tool()
async def get_transaction_history(
    account_id: str,
    min_row: Optional[int] = None,
    max_row: Optional[int] = None,
) -> Dict[str, Any]:
    """Get transaction history for an account.

    Args:
        account_id: ID of the account to get transactions for
        min_row: Minimum row number (optional, for pagination)
        max_row: Maximum row number (optional, for pagination)

    Returns:
        Dictionary containing transaction history for the specified account.
    """
    client = await get_client()
    try:
        return await client.get_transactions(account_id, min_row, max_row)
    except Exception as e:
        logger.error(f"Error getting transaction history for {account_id}: {e}")
        return {"error": str(e), "account_id": account_id}


@mcp.tool()
async def get_fees(pair: str) -> Dict[str, Any]:
    """Get fee information for a trading pair.

    Args:
        pair: Trading pair (e.g., 'XBTZAR', 'ETHZAR')

    Returns:
        Dictionary containing fee information for the specified trading pair.
    """
    client = await get_client()
    try:
        return await client.get_fee_info(pair)
    except Exception as e:
        logger.error(f"Error getting fees for {pair}: {e}")
        return {"error": str(e), "pair": pair}


async def cleanup():
    """Cleanup resources when server shuts down."""
    global client
    if client:
        await client.close()
        logger.info("Luno client closed")


if __name__ == "__main__":
    # Run the FastMCP server with proper stdio transport
    logger.info("Starting Luno MCP Server with FastMCP")

    # Log credential status
    api_key = os.environ.get("LUNO_API_KEY")
    api_secret = os.environ.get("LUNO_API_SECRET")

    if api_key and api_secret:
        logger.info("API credentials found in environment configuration")
    else:
        logger.warning("No API credentials found - only public endpoints available")
        logger.info(
            "Set LUNO_API_KEY and LUNO_API_SECRET environment variables for full functionality"
        )

    # Log level configuration
    log_level = os.environ.get("LUNO_MCP_LOG_LEVEL", "INFO")
    logger.info(f"Log level set to: {log_level}")

    # Transport information
    logger.info("Using STDIO transport")

    # Run the server
    mcp.run(transport="stdio")

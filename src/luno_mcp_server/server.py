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


@mcp.tool()
async def get_historical_prices(
    pair: str,
    since: int,
    duration: int = 86400,
) -> Dict[str, Any]:
    """Get historical price data (OHLC candlestick data) for a trading pair.

    Args:
        pair: Trading pair (e.g., 'XBTZAR', 'ETHZAR')
        since: Start timestamp in Unix milliseconds (up to 1000 candles will be returned)
        duration: Candle duration in seconds. Supported values:
                 60 (1m), 300 (5m), 900 (15m), 1800 (30m), 3600 (1h),
                 10800 (3h), 14400 (4h), 28800 (8h), 86400 (24h),
                 259200 (3d), 604800 (7d). Default: 86400 (24h)

    Returns:
        Dictionary containing historical candlestick data with OHLC prices and volume.
    """
    client = await get_client()
    try:
        candles = await client.get_candles(pair, since, duration)

        duration_name = _get_duration_name(duration)

        return {
            "pair": pair.upper(),
            "since": since,
            "duration": duration,
            "duration_name": duration_name,
            "candles": candles.get("candles", []),
            "candle_count": len(candles.get("candles", [])),
            "status": "success",
        }
    except Exception as e:
        logger.error(f"Error getting historical prices for {pair}: {e}")
        return {
            "pair": pair,
            "since": since,
            "duration": duration,
            "error": str(e),
            "status": "error",
        }


@mcp.tool()
async def get_price_range(
    pair: str,
    days: int = 7,
) -> Dict[str, Any]:
    """Get price range analysis for a trading pair over a specified number of days.

    Args:
        pair: Trading pair (e.g., 'XBTZAR', 'ETHZAR')
        days: Number of days of historical data to retrieve (1-30). Default: 7

    Returns:
        Dictionary containing price statistics including high, low, open, close prices
        and percentage changes over the specified time period.
    """
    client = await get_client()
    try:
        # Validate days parameter
        if days < 1 or days > 30:
            return {
                "pair": pair,
                "error": "Days parameter must be between 1 and 30",
                "status": "error",
            }

        # Calculate since timestamp (days ago)
        from datetime import datetime, timezone, timedelta

        since_dt = datetime.now(timezone.utc) - timedelta(days=days)
        since = int(since_dt.timestamp() * 1000)

        # Get daily candles (86400 seconds = 24 hours)
        candles_data = await client.get_candles(pair, since, 86400)
        candles = candles_data.get("candles", [])

        if not candles:
            return {
                "pair": pair.upper(),
                "days": days,
                "error": "No historical data available for the specified period",
                "status": "error",
            }

        # Calculate price statistics
        prices = [float(candle["close"]) for candle in candles]
        highs = [float(candle["high"]) for candle in candles]
        lows = [float(candle["low"]) for candle in candles]
        volumes = [float(candle["volume"]) for candle in candles]

        first_candle = candles[0]
        last_candle = candles[-1]

        open_price = float(first_candle["open"])
        close_price = float(last_candle["close"])
        price_change = close_price - open_price
        price_change_percent = (
            (price_change / open_price) * 100 if open_price > 0 else 0
        )

        return {
            "pair": pair.upper(),
            "days": days,
            "period_start": first_candle["timestamp"],
            "period_end": last_candle["timestamp"],
            "open_price": str(open_price),
            "close_price": str(close_price),
            "highest_price": str(max(highs)),
            "lowest_price": str(min(lows)),
            "price_change": str(price_change),
            "price_change_percent": f"{price_change_percent:.2f}%",
            "average_price": str(sum(prices) / len(prices)),
            "total_volume": str(sum(volumes)),
            "candle_count": len(candles),
            "status": "success",
        }
    except Exception as e:
        logger.error(f"Error getting price range for {pair}: {e}")
        return {
            "pair": pair,
            "days": days,
            "error": str(e),
            "status": "error",
        }


def _get_duration_name(duration: int) -> str:
    """Convert duration in seconds to human-readable name."""
    duration_map = {
        60: "1m",
        300: "5m",
        900: "15m",
        1800: "30m",
        3600: "1h",
        10800: "3h",
        14400: "4h",
        28800: "8h",
        86400: "24h",
        259200: "3d",
        604800: "7d",
    }
    return duration_map.get(duration, f"{duration}s")


@mcp.tool()
async def get_support_info() -> Dict[str, Any]:
    """Get information about supporting the Luno MCP Server project.

    Returns:
        Dictionary containing donation and support information for the project.
    """
    return {
        "project": "Luno MCP Server",
        "description": "Open source Model Context Protocol server for Luno cryptocurrency exchange",
        "support_message": "Help keep this free trading tool growing! All donation options work globally. 🌍",
        "global_donation_options": {
            "buy_me_coffee": {
                "url": "https://buymeacoffee.com/amanasmuei",
                "description": "Most popular platform - works in 190+ countries",
                "features": [
                    "PayPal",
                    "Stripe",
                    "Local payments",
                    "Monthly memberships",
                ],
            },
            "kofi": {
                "url": "https://ko-fi.com/amanasmuei",
                "description": "Creator-friendly platform with global reach",
                "features": ["One-time donations", "Monthly memberships"],
            },
            "github_sponsors": {
                "url": "https://github.com/sponsors/amanasmuei",
                "description": "Monthly or one-time sponsorship through GitHub",
                "features": ["Integrated with development", "Professional"],
            },
            "paypal_me": {
                "url": "https://paypal.me/amanasmuei",
                "description": "Direct PayPal payment - works in most countries",
                "features": ["Instant payments", "No setup required"],
            },
            "lightning_network": {
                "address": "yourlightningaddress@domain.com",
                "description": "Ultra-fast Bitcoin micropayments",
                "features": ["Instant settlement", "Low fees"],
            },
        },
        "crypto_donations": {
            "bitcoin": "3CPb1HP6Gfpx3MZFdrm4nhoHk4VbX2eZRj",
            "ethereum": "0x54dC4eDf6c940C52A1434824634d8cE8629767b3",
            "lightning": "yourlightningaddress@domain.com",
            "note": "Perfect for a crypto trading project!",
        },
        "free_support": {
            "github_star": "https://github.com/amanasmuei/luno-mcp",
            "share_project": "Tell other crypto traders about this tool",
            "contribute": "Submit pull requests and improvements",
        },
        "what_support_enables": [
            "New trading pair integrations",
            "Advanced analytics and indicators",
            "Performance optimizations",
            "Bug fixes and security updates",
            "Comprehensive documentation",
            "Community support and tutorials",
        ],
        "donation_page": "./docs/donate.html",
        "status": "Thank you for considering supporting this open source project! 🚀",
    }


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

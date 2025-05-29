"""
Market data tools for the Luno MCP server.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from fastmcp.server.context import Context
from pydantic import Field
from typing_extensions import Annotated

from ..client import LunoClient, LunoAPIError

logger = logging.getLogger(__name__)


def register_market_tools(mcp: FastMCP, client: LunoClient) -> None:
    """Register all market-related tools with the FastMCP server."""

    @mcp.tool()
    async def get_crypto_price(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Get current price information for a cryptocurrency trading pair.

        This tool provides real-time market data including ask/bid prices,
        last trade information, and 24-hour volume data.
        """
        try:
            await ctx.debug(f"Fetching price data for trading pair: {pair}")

            ticker = await client.get_ticker(pair)

            result = {
                "pair": pair.upper(),
                "ask": ticker.get("ask"),
                "bid": ticker.get("bid"),
                "last_trade": ticker.get("last_trade"),
                "rolling_24_hour_volume": ticker.get("rolling_24_hour_volume"),
                "timestamp": ticker.get("timestamp"),
                "status": "success",
            }

            await ctx.info(f"Successfully retrieved price data for {pair}")
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting price for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting price for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_market_overview(ctx: Context) -> Dict[str, Any]:
        """
        Get an overview of all available cryptocurrency markets on Luno.

        This tool provides a comprehensive summary of all trading markets,
        including available trading pairs and market information.
        """
        try:
            await ctx.debug("Fetching market overview data")

            markets = await client.get_market_summary()

            result = {
                "markets": markets,
                "total_markets": (
                    len(markets.get("markets", []))
                    if isinstance(markets.get("markets"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info("Successfully retrieved market overview")
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting market overview: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error getting market overview: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_orderbook(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Get the order book (buy and sell orders) for a trading pair.

        This tool provides current market depth information showing
        pending buy and sell orders at different price levels.
        """
        try:
            await ctx.debug(f"Fetching orderbook for trading pair: {pair}")

            orderbook = await client.get_orderbook(pair)

            result = {
                "pair": pair.upper(),
                "orderbook": orderbook,
                "bid_count": len(orderbook.get("bids", [])),
                "ask_count": len(orderbook.get("asks", [])),
                "status": "success",
            }

            await ctx.info(f"Successfully retrieved orderbook for {pair}")
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting orderbook for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting orderbook for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_recent_trades(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
        since: Annotated[
            Optional[int],
            Field(description="Unix timestamp to get trades since (optional)"),
        ] = None,
    ) -> Dict[str, Any]:
        """
        Get recent trades for a trading pair.

        This tool provides historical trade data showing recent market activity
        including trade prices, volumes, and timestamps.
        """
        try:
            await ctx.debug(
                f"Fetching recent trades for {pair}"
                + (f" since {since}" if since else "")
            )

            trades = await client.get_trades(pair, since)

            result = {
                "pair": pair.upper(),
                "trades": trades,
                "trade_count": (
                    len(trades.get("trades", []))
                    if isinstance(trades.get("trades"), list)
                    else 0
                ),
                "since": since,
                "status": "success",
            }

            await ctx.info(f"Successfully retrieved recent trades for {pair}")
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting trades for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting trades for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_all_tickers(ctx: Context) -> Dict[str, Any]:
        """
        Get ticker information for all available trading pairs.

        This tool provides current price information for all cryptocurrency
        pairs available on the Luno exchange.
        """
        try:
            await ctx.debug("Fetching all ticker information")

            tickers = await client.get_tickers()

            result = {
                "tickers": tickers,
                "ticker_count": (
                    len(tickers.get("tickers", []))
                    if isinstance(tickers.get("tickers"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info("Successfully retrieved all tickers")
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting all tickers: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error getting all tickers: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

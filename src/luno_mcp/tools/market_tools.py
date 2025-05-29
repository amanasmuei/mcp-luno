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

    @mcp.tool()
    async def get_historical_prices(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        since: Annotated[
            int,
            Field(
                description="Start timestamp in Unix milliseconds (up to 1000 candles will be returned)"
            ),
        ],
        ctx: Context,
        duration: Annotated[
            int,
            Field(
                description="Candle duration in seconds. Supported: 60 (1m), 300 (5m), 900 (15m), 1800 (30m), 3600 (1h), 10800 (3h), 14400 (4h), 28800 (8h), 86400 (24h), 259200 (3d), 604800 (7d)"
            ),
        ] = 86400,  # Default to 24h candles
    ) -> Dict[str, Any]:
        """
        Get historical price data (OHLC candlestick data) for a trading pair.

        This tool provides historical market data in candlestick format showing
        open, high, low, close prices and volume for specified time periods.
        Returns up to 1000 of the earliest candles from the specified start time.
        """
        try:
            await ctx.debug(
                f"Fetching historical price data for {pair} since {since} with {duration}s duration"
            )

            candles = await client.get_candles(pair, since, duration)

            result = {
                "pair": pair.upper(),
                "since": since,
                "duration": duration,
                "duration_name": _get_duration_name(duration),
                "candles": candles.get("candles", []),
                "candle_count": len(candles.get("candles", [])),
                "status": "success",
            }

            await ctx.info(
                f"Successfully retrieved {result['candle_count']} historical candles for {pair}"
            )
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting historical prices for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "since": since,
                "duration": duration,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting historical prices for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "since": since,
                "duration": duration,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_price_range(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
        days: Annotated[
            int,
            Field(description="Number of days of historical data to retrieve (1-30)"),
        ] = 7,
    ) -> Dict[str, Any]:
        """
        Get price range analysis for a trading pair over a specified number of days.

        This tool provides a convenient way to get recent price statistics including
        high, low, open, close prices and percentage changes over a time period.
        Uses daily candles for the analysis.
        """
        try:
            # Validate days parameter
            if days < 1 or days > 30:
                return {
                    "pair": pair,
                    "error": "Days parameter must be between 1 and 30",
                    "status": "error",
                    "error_type": "validation_error",
                }

            await ctx.debug(
                f"Fetching price range analysis for {pair} over {days} days"
            )

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
                    "error_type": "no_data",
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

            result = {
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

            await ctx.info(
                f"Successfully calculated price range for {pair} over {days} days"
            )
            return result

        except LunoAPIError as e:
            error_msg = f"Luno API error getting price range for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "days": days,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting price range for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "days": days,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
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

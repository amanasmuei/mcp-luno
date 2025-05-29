"""
Trading tools for the Luno MCP server.
"""

import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from fastmcp.server.context import Context
from pydantic import Field
from typing_extensions import Annotated

from ..client import LunoClient, LunoAPIError, LunoAuthenticationError
from ..config import has_credentials

logger = logging.getLogger(__name__)


def register_trading_tools(mcp: FastMCP, client: LunoClient) -> None:
    """Register all trading-related tools with the FastMCP server."""

    @mcp.tool()
    async def place_order(
        order_type: Annotated[
            str, Field(description="Order type: 'BID' for buy, 'ASK' for sell")
        ],
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
        price: Annotated[
            Optional[str],
            Field(description="Price per unit (optional for market orders)"),
        ] = None,
        volume: Annotated[
            Optional[str],
            Field(description="Amount to trade (optional, use for limit orders)"),
        ] = None,
        base_account_id: Annotated[
            Optional[str], Field(description="Base currency account ID (optional)")
        ] = None,
        counter_account_id: Annotated[
            Optional[str], Field(description="Counter currency account ID (optional)")
        ] = None,
    ) -> Dict[str, Any]:
        """
        Place a new trading order on the Luno exchange.

        This tool allows placing buy (BID) or sell (ASK) orders.
        Requires authentication with valid API credentials.
        """
        try:
            # Check if credentials are available
            if not has_credentials():
                await ctx.error("Authentication required: API credentials not found")
                return {
                    "error": "This tool requires authentication. Please provide LUNO_API_KEY and LUNO_API_SECRET.",
                    "status": "error",
                    "error_type": "authentication_required",
                }

            await ctx.debug(f"Placing {order_type} order for {pair}")
            await ctx.info(
                f"Order details - Type: {order_type}, Pair: {pair}, Price: {price}, Volume: {volume}"
            )

            order = await client.create_order(
                order_type=order_type,
                pair=pair,
                price=price,
                volume=volume,
                base_account_id=base_account_id,
                counter_account_id=counter_account_id,
            )

            result = {
                "order": order,
                "order_type": order_type.upper(),
                "pair": pair.upper(),
                "status": "success",
            }

            await ctx.info(
                f"Successfully placed order: {order.get('order_id', 'Unknown ID')}"
            )
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error placing order: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error placing order: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error placing order: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def cancel_order(
        order_id: Annotated[str, Field(description="ID of the order to cancel")],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Cancel an existing order on the Luno exchange.

        This tool cancels a pending order by its ID.
        Requires authentication with valid API credentials.
        """
        try:
            # Check if credentials are available
            if not has_credentials():
                await ctx.error("Authentication required: API credentials not found")
                return {
                    "error": "This tool requires authentication. Please provide LUNO_API_KEY and LUNO_API_SECRET.",
                    "status": "error",
                    "error_type": "authentication_required",
                }

            await ctx.debug(f"Cancelling order: {order_id}")

            result_data = await client.cancel_order(order_id)

            result = {
                "cancellation": result_data,
                "order_id": order_id,
                "status": "success",
            }

            await ctx.info(f"Successfully cancelled order: {order_id}")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error cancelling order {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error cancelling order {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error cancelling order {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_order_status(
        order_id: Annotated[str, Field(description="ID of the order to check")],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Get the status and details of a specific order.

        This tool provides detailed information about an order including
        its current status, filled amount, and other relevant details.
        Requires authentication with valid API credentials.
        """
        try:
            # Check if credentials are available
            if not has_credentials():
                await ctx.error("Authentication required: API credentials not found")
                return {
                    "error": "This tool requires authentication. Please provide LUNO_API_KEY and LUNO_API_SECRET.",
                    "status": "error",
                    "error_type": "authentication_required",
                }

            await ctx.debug(f"Fetching status for order: {order_id}")

            order = await client.get_order(order_id)

            result = {"order": order, "order_id": order_id, "status": "success"}

            await ctx.info(f"Successfully retrieved order status for: {order_id}")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting order status for {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error getting order status for {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting order status for {order_id}: {e}"
            await ctx.error(error_msg)
            return {
                "order_id": order_id,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_open_orders(
        ctx: Context,
        pair: Annotated[
            Optional[str], Field(description="Filter by trading pair (optional)")
        ] = None,
        state: Annotated[
            Optional[str], Field(description="Filter by order state (optional)")
        ] = None,
    ) -> Dict[str, Any]:
        """
        Get list of open/pending orders.

        This tool retrieves all current orders, optionally filtered by
        trading pair or order state.
        Requires authentication with valid API credentials.
        """
        try:
            # Check if credentials are available
            if not has_credentials():
                await ctx.error("Authentication required: API credentials not found")
                return {
                    "error": "This tool requires authentication. Please provide LUNO_API_KEY and LUNO_API_SECRET.",
                    "status": "error",
                    "error_type": "authentication_required",
                }

            filter_msg = []
            if pair:
                filter_msg.append(f"pair: {pair}")
            if state:
                filter_msg.append(f"state: {state}")

            filter_str = (
                f" with filters ({', '.join(filter_msg)})" if filter_msg else ""
            )
            await ctx.debug(f"Fetching open orders{filter_str}")

            orders = await client.get_orders(state=state, pair=pair)

            result = {
                "orders": orders,
                "filter_pair": pair,
                "filter_state": state,
                "order_count": (
                    len(orders.get("orders", []))
                    if isinstance(orders.get("orders"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info(f"Successfully retrieved open orders{filter_str}")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting open orders: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error getting open orders: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error getting open orders: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_fees(
        pair: Annotated[
            str, Field(description="Trading pair (e.g., 'XBTZAR', 'ETHZAR')")
        ],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Get fee information for a trading pair.

        This tool provides current trading fees for the specified pair.
        Requires authentication with valid API credentials.
        """
        try:
            # Check if credentials are available
            if not has_credentials():
                await ctx.error("Authentication required: API credentials not found")
                return {
                    "error": "This tool requires authentication. Please provide LUNO_API_KEY and LUNO_API_SECRET.",
                    "status": "error",
                    "error_type": "authentication_required",
                }

            await ctx.debug(f"Fetching fee information for: {pair}")

            fees = await client.get_fee_info(pair)

            result = {"fees": fees, "pair": pair.upper(), "status": "success"}

            await ctx.info(f"Successfully retrieved fee information for: {pair}")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting fees for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error getting fees for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = f"Unexpected error getting fees for {pair}: {e}"
            await ctx.error(error_msg)
            return {
                "pair": pair,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

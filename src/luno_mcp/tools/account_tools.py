"""
Account management tools for the Luno MCP server.
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


def register_account_tools(mcp: FastMCP, client: LunoClient) -> None:
    """Register all account-related tools with the FastMCP server."""

    @mcp.tool()
    async def get_account_balance(ctx: Context) -> Dict[str, Any]:
        """
        Get account balances for all currencies.

        This tool provides current balance information for all currencies
        in your Luno account, including available and reserved amounts.
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

            await ctx.debug("Fetching account balances")

            balances = await client.get_balances()

            result = {
                "balances": balances,
                "balance_count": (
                    len(balances.get("balance", []))
                    if isinstance(balances.get("balance"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info("Successfully retrieved account balances")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting account balances: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error getting account balances: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error getting account balances: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_accounts(ctx: Context) -> Dict[str, Any]:
        """
        Get detailed information about all accounts.

        This tool provides comprehensive account information including
        account IDs, currencies, and account details.
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

            await ctx.debug("Fetching account information")

            accounts = await client.get_accounts()

            result = {
                "accounts": accounts,
                "account_count": (
                    len(accounts.get("balance", []))
                    if isinstance(accounts.get("balance"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info("Successfully retrieved account information")
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting accounts: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = f"Luno API error getting accounts: {e}"
            await ctx.error(error_msg)
            return {"error": str(e), "status": "error", "error_type": "api_error"}
        except Exception as e:
            error_msg = f"Unexpected error getting accounts: {e}"
            await ctx.error(error_msg)
            return {
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_transaction_history(
        account_id: Annotated[
            str, Field(description="Account ID to get transaction history for")
        ],
        ctx: Context,
        min_row: Annotated[
            Optional[int],
            Field(description="Minimum row number for pagination (optional)"),
        ] = None,
        max_row: Annotated[
            Optional[int],
            Field(description="Maximum row number for pagination (optional)"),
        ] = None,
    ) -> Dict[str, Any]:
        """
        Get transaction history for a specific account.

        This tool provides historical transaction data for an account,
        with optional pagination using min_row and max_row parameters.
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

            pagination_info = []
            if min_row is not None:
                pagination_info.append(f"min_row: {min_row}")
            if max_row is not None:
                pagination_info.append(f"max_row: {max_row}")

            pagination_str = (
                f" with pagination ({', '.join(pagination_info)})"
                if pagination_info
                else ""
            )
            await ctx.debug(
                f"Fetching transaction history for account {account_id}{pagination_str}"
            )

            transactions = await client.get_transactions(account_id, min_row, max_row)

            result = {
                "transactions": transactions,
                "account_id": account_id,
                "min_row": min_row,
                "max_row": max_row,
                "transaction_count": (
                    len(transactions.get("transactions", []))
                    if isinstance(transactions.get("transactions"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info(
                f"Successfully retrieved transaction history for account {account_id}"
            )
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting transaction history for {account_id}: {e}"
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = (
                f"Luno API error getting transaction history for {account_id}: {e}"
            )
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = (
                f"Unexpected error getting transaction history for {account_id}: {e}"
            )
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def get_pending_transactions(
        account_id: Annotated[
            str, Field(description="Account ID to get pending transactions for")
        ],
        ctx: Context,
    ) -> Dict[str, Any]:
        """
        Get pending transactions for a specific account.

        This tool provides information about transactions that are currently
        pending or being processed for the specified account.
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

            await ctx.debug(f"Fetching pending transactions for account {account_id}")

            pending = await client.get_pending_transactions(account_id)

            result = {
                "pending_transactions": pending,
                "account_id": account_id,
                "pending_count": (
                    len(pending.get("pending", []))
                    if isinstance(pending.get("pending"), list)
                    else 0
                ),
                "status": "success",
            }

            await ctx.info(
                f"Successfully retrieved pending transactions for account {account_id}"
            )
            return result

        except LunoAuthenticationError as e:
            error_msg = f"Authentication error getting pending transactions for {account_id}: {e}"
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "authentication_error",
            }
        except LunoAPIError as e:
            error_msg = (
                f"Luno API error getting pending transactions for {account_id}: {e}"
            )
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "api_error",
            }
        except Exception as e:
            error_msg = (
                f"Unexpected error getting pending transactions for {account_id}: {e}"
            )
            await ctx.error(error_msg)
            return {
                "account_id": account_id,
                "error": str(e),
                "status": "error",
                "error_type": "unexpected_error",
            }

    @mcp.tool()
    async def check_api_health(ctx: Context) -> Dict[str, Any]:
        """
        Check the health and connectivity of the Luno API.

        This tool performs a basic health check to verify that the API
        is accessible and responding properly. Does not require authentication.
        """
        try:
            await ctx.debug("Performing API health check")

            is_healthy = await client.health_check()

            result = {
                "api_healthy": is_healthy,
                "status": "success" if is_healthy else "warning",
                "message": (
                    "API is responding normally"
                    if is_healthy
                    else "API may be experiencing issues"
                ),
            }

            if is_healthy:
                await ctx.info("API health check passed")
            else:
                await ctx.warning("API health check failed")

            return result

        except Exception as e:
            error_msg = f"Error during API health check: {e}"
            await ctx.error(error_msg)
            return {
                "api_healthy": False,
                "error": str(e),
                "status": "error",
                "error_type": "health_check_failed",
            }

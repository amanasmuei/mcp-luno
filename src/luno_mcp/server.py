"""
Modern FastMCP server implementation for the Luno API.

This module creates and configures the main FastMCP server with all tools,
resources, and proper error handling using current best practices.
"""

import logging
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.context import Context

from .config import LunoMCPConfig, get_config, has_credentials
from .client import LunoClient
from .tools import register_market_tools, register_trading_tools, register_account_tools

logger = logging.getLogger(__name__)

# Global instances
_config: Optional[LunoMCPConfig] = None
_client: Optional[LunoClient] = None


async def get_luno_client() -> LunoClient:
    """Get or create the global Luno client instance."""
    global _client, _config

    if _client is None:
        _config = get_config()
        _client = LunoClient(_config)

        # Log configuration status
        if has_credentials(_config):
            logger.info("Luno client initialized with authentication")
        else:
            logger.warning(
                "Luno client initialized without authentication - only public endpoints available"
            )

    return _client


async def cleanup_client() -> None:
    """Cleanup the global client instance."""
    global _client

    if _client:
        await _client.close()
        _client = None
        logger.info("Luno client cleaned up")


def create_server(config: Optional[LunoMCPConfig] = None) -> FastMCP:
    """
    Create and configure the FastMCP server with all tools and resources.

    Args:
        config: Optional configuration. If not provided, will be loaded from environment.

    Returns:
        Configured FastMCP server instance.
    """
    # Use provided config or load from environment
    server_config = config or get_config()

    # Create FastMCP server instance
    mcp = FastMCP(
        name=server_config.server_name, description=server_config.server_description
    )

    # Set up logging level
    logging.getLogger().setLevel(getattr(logging, server_config.log_level.value))

    @mcp.resource("luno://config")
    async def get_server_config(ctx: Context) -> dict:
        """
        Get current server configuration (excluding sensitive data).

        This resource provides information about the current server
        configuration without exposing API credentials.
        """
        await ctx.debug("Providing server configuration")

        return {
            "server_name": server_config.server_name,
            "server_description": server_config.server_description,
            "transport": server_config.transport.value,
            "host": server_config.host,
            "port": server_config.port,
            "log_level": server_config.log_level.value,
            "api_base_url": server_config.api_base_url,
            "request_timeout": server_config.request_timeout,
            "max_requests_per_minute": server_config.max_requests_per_minute,
            "has_credentials": has_credentials(server_config),
            "version": "0.2.0",
        }

    @mcp.resource("luno://status")
    async def get_server_status(ctx: Context) -> dict:
        """
        Get current server status and health information.

        This resource provides real-time status information about
        the server and its connection to the Luno API.
        """
        await ctx.debug("Checking server status")

        try:
            client = await get_luno_client()
            api_healthy = await client.health_check()

            return {
                "server_healthy": True,
                "api_healthy": api_healthy,
                "has_credentials": has_credentials(server_config),
                "client_initialized": _client is not None,
                "timestamp": str(asyncio.get_event_loop().time()),
            }
        except Exception as e:
            await ctx.error(f"Error checking server status: {e}")
            return {
                "server_healthy": False,
                "api_healthy": False,
                "error": str(e),
                "timestamp": str(asyncio.get_event_loop().time()),
            }

    @mcp.resource("luno://endpoints")
    async def get_available_endpoints(ctx: Context) -> dict:
        """
        Get information about available API endpoints and tools.

        This resource provides a summary of all available tools
        and their authentication requirements.
        """
        await ctx.debug("Listing available endpoints")

        endpoints = {
            "public_endpoints": {
                "description": "These endpoints do not require authentication",
                "tools": [
                    "get_crypto_price",
                    "get_market_overview",
                    "get_orderbook",
                    "get_recent_trades",
                    "get_all_tickers",
                    "check_api_health",
                ],
            },
            "private_endpoints": {
                "description": "These endpoints require API credentials",
                "tools": [
                    "get_account_balance",
                    "get_accounts",
                    "get_transaction_history",
                    "get_pending_transactions",
                    "place_order",
                    "cancel_order",
                    "get_order_status",
                    "get_open_orders",
                    "get_fees",
                ],
                "authentication_available": has_credentials(server_config),
            },
        }

        return endpoints

    # Initialize and register tools
    async def setup_tools():
        """Setup and register all tools with the server."""
        try:
            client = await get_luno_client()

            # Register tool categories
            register_market_tools(mcp, client)
            register_trading_tools(mcp, client)
            register_account_tools(mcp, client)

            logger.info("All tools registered successfully")

        except Exception as e:
            logger.error(f"Error setting up tools: {e}")
            raise

    # Set up the tools during server initialization
    # Note: We'll call this when the server actually starts
    mcp._setup_tools = setup_tools

    return mcp


async def run_server(
    config: Optional[LunoMCPConfig] = None,
    transport: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> None:
    """
    Run the FastMCP server with the specified configuration.

    Args:
        config: Optional server configuration
        transport: Optional transport override
        host: Optional host override
        port: Optional port override
    """
    server_config = config or get_config()

    # Override config with provided parameters
    if transport:
        server_config.transport = transport
    if host:
        server_config.host = host
    if port:
        server_config.port = port

    # Create the server
    mcp = create_server(server_config)

    try:
        # Setup tools
        if hasattr(mcp, "_setup_tools"):
            await mcp._setup_tools()

        logger.info(f"Starting Luno MCP server on {server_config.transport.value}")
        if server_config.transport.value in ["streamable-http", "sse"]:
            logger.info(
                f"Server will be available at {server_config.host}:{server_config.port}"
            )

        # Run the server based on transport type
        if server_config.transport.value == "stdio":
            await mcp.run_async(transport="stdio")
        elif server_config.transport.value == "streamable-http":
            await mcp.run_async(
                transport="streamable-http",
                host=server_config.host,
                port=server_config.port,
            )
        elif server_config.transport.value == "sse":
            await mcp.run_async(
                transport="sse", host=server_config.host, port=server_config.port
            )
        else:
            raise ValueError(f"Unsupported transport: {server_config.transport}")

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise
    finally:
        await cleanup_client()


# Legacy compatibility - export the server instance
mcp = None


def get_server() -> FastMCP:
    """Get the default server instance for backwards compatibility."""
    global mcp
    if mcp is None:
        mcp = create_server()

        # Setup tools synchronously for compatibility
        async def setup():
            if hasattr(mcp, "_setup_tools"):
                await mcp._setup_tools()

        # Try to setup tools if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule for later execution
                asyncio.create_task(setup())
            else:
                loop.run_until_complete(setup())
        except RuntimeError:
            # No event loop available, will setup when server runs
            pass

    return mcp


# For backwards compatibility
async def cleanup():
    """Legacy cleanup function."""
    await cleanup_client()


# Create default instance for backwards compatibility
mcp = get_server()

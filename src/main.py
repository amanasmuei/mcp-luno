"""
Main entry point for the Luno MCP server using the refactored FastMCP implementation.

This script provides both async and sync entry points for running the server
with various transport options and configurations.
"""

import os
import asyncio
import logging
import sys
import argparse
from typing import Optional

from dotenv import load_dotenv

from luno_mcp.config import LunoMCPConfig, TransportType, LogLevel
from luno_mcp.server import run_server, create_server

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Luno MCP Server - FastMCP implementation for Luno cryptocurrency exchange API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --transport stdio
  python src/main.py --transport streamable-http --host 0.0.0.0 --port 8080
  python src/main.py --transport sse --port 9000 --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--transport",
        "-t",
        type=str,
        choices=[t.value for t in TransportType],
        default=os.environ.get("LUNO_MCP_TRANSPORT", TransportType.STDIO.value),
        help="Transport mechanism to use (default: %(default)s)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("LUNO_MCP_HOST", "localhost"),
        help="Host to bind to for HTTP-based transports (default: %(default)s)",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.environ.get("LUNO_MCP_PORT", "8000")),
        help="Port to bind to for HTTP-based transports (default: %(default)s)",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        choices=[l.value for l in LogLevel],
        default=os.environ.get("LUNO_MCP_LOG_LEVEL", LogLevel.INFO.value),
        help="Logging level (default: %(default)s)",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("LUNO_API_KEY"),
        help="Luno API key (can also be set via LUNO_API_KEY environment variable)",
    )

    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("LUNO_API_SECRET"),
        help="Luno API secret (can also be set via LUNO_API_SECRET environment variable)",
    )

    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to configuration file (optional)",
    )

    parser.add_argument(
        "--version", "-v", action="version", version="Luno MCP Server 0.2.0"
    )

    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> LunoMCPConfig:
    """Create configuration from command line arguments."""
    config_data = {
        "transport": args.transport,
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
    }

    # Add API credentials if provided
    if args.api_key:
        config_data["api_key"] = args.api_key
    if args.api_secret:
        config_data["api_secret"] = args.api_secret

    return LunoMCPConfig(**config_data)


async def main() -> None:
    """Main async entry point for the MCP server."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Create configuration
        config = create_config_from_args(args)

        # Set logging level
        logging.getLogger().setLevel(getattr(logging, config.log_level.value))

        # Log startup information
        logger.info("Starting Luno MCP server...")
        logger.info(f"Server: {config.server_name}")
        logger.info(f"Transport: {config.transport.value}")
        logger.info(f"Log level: {config.log_level.value}")

        # Log authentication status
        if config.api_key and config.api_secret:
            logger.info("API credentials configured - all endpoints available")
        else:
            logger.warning(
                "No API credentials configured - only public endpoints available"
            )
            logger.info(
                "Set LUNO_API_KEY and LUNO_API_SECRET environment variables or use --api-key/--api-secret arguments"
            )

        # Log transport-specific information
        if config.transport.value in ["streamable-http", "sse"]:
            logger.info(
                f"Server will be available at http://{config.host}:{config.port}"
            )

        # Run the server
        await run_server(config=config)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


def run_sync() -> None:
    """
    Synchronous entry point that runs the async main function.

    This is the main entry point used by setuptools console scripts
    and for compatibility with various deployment scenarios.
    """
    try:
        # Parse arguments for early validation
        args = parse_arguments()
        config = create_config_from_args(args)

        # Set logging level early
        logging.getLogger().setLevel(getattr(logging, config.log_level.value))

        logger.info("Starting Luno MCP server...")

        # Log authentication status
        if config.api_key and config.api_secret:
            logger.info("API credentials configured - all endpoints available")
        else:
            logger.warning(
                "No API credentials configured - only public endpoints available"
            )

        # For stdio transport, use the legacy compatibility mode
        if config.transport.value == "stdio":
            # Import and use the legacy server for stdio compatibility
            from luno_mcp.server import get_server

            server = get_server()
            server.run(transport="stdio")
        else:
            # Use modern async approach for HTTP-based transports
            asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


def dev_mode() -> None:
    """Entry point for development mode with enhanced logging."""
    # Force debug logging in dev mode
    os.environ["LUNO_MCP_LOG_LEVEL"] = "DEBUG"

    logger.info("Running in development mode with debug logging")
    run_sync()


if __name__ == "__main__":
    run_sync()

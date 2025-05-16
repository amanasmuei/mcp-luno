"""
Main entry point for the Luno MCP server.

This script starts the MCP server with the configured transport mechanism.
"""

import os
import asyncio
import logging
import sys
import argparse
from dotenv import load_dotenv
from src.luno_mcp_server.server import LunoMCPServer

# Load environment variables from .env file (lowest priority)
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Luno MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "websocket"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="Transport mechanism to use (stdio or websocket)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCP_HOST", "localhost"),
        help="Host to bind to when using websocket transport",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8765")),
        help="Port to bind to when using websocket transport",
    )
    parser.add_argument(
        "--max-connections",
        type=int,
        default=int(os.environ.get("MCP_MAX_CONNECTIONS", "50")),
        help="Maximum number of concurrent connections (websocket only)",
    )
    parser.add_argument(
        "--max-message-size",
        type=int,
        default=int(os.environ.get("MCP_MAX_MESSAGE_SIZE", "1048576")),  # 1MB default
        help="Maximum message size in bytes (websocket only)",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=int(os.environ.get("MCP_RATE_LIMIT", "100")),
        help="Maximum number of messages per minute per client (websocket only)",
    )
    parser.add_argument(
        "--ssl-cert",
        type=str,
        default=os.environ.get("SSL_CERT_PATH", "./certs/server.crt"),
        help="Path to SSL certificate file for secure WebSocket",
    )
    parser.add_argument(
        "--ssl-key",
        type=str,
        default=os.environ.get("SSL_KEY_PATH", "./certs/server.key"),
        help="Path to SSL key file for secure WebSocket",
    )
    return parser.parse_args()


async def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    args = parse_arguments()

    logger.info("Starting Luno MCP server...")

    # Log configuration source
    api_key_exists = bool(os.environ.get("LUNO_API_KEY"))
    api_secret_exists = bool(os.environ.get("LUNO_API_SECRET"))
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    # Set log level based on environment
    logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))

    # Log configuration information
    if api_key_exists and api_secret_exists:
        logger.info("API credentials found in environment configuration")
    else:
        logger.warning(
            "No API credentials found in environment - only public endpoints will be available"
        )

    logger.info(f"Log level set to: {log_level}")

    # Log transport information
    if args.transport == "websocket":
        logger.info(f"Using WebSocket transport on {args.host}:{args.port}")
    else:
        logger.info("Using STDIO transport")

    # Initialize and run the server with the specified transport
    server = LunoMCPServer()

    if args.transport == "websocket":
        # Set SSL environment variables for the WebSocketTransport
        os.environ["SSL_CERT_PATH"] = args.ssl_cert
        os.environ["SSL_KEY_PATH"] = args.ssl_key
        await server.run(
            transport_type=args.transport,
            host=args.host,
            port=args.port,
            max_connections=args.max_connections,
            max_message_size=args.max_message_size,
            rate_limit=args.rate_limit,
        )
    else:
        await server.run(transport_type=args.transport)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)

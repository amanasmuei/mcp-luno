"""
Main entry point for the Luno MCP server.
"""

import os
import asyncio
import logging
import sys
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


async def main():
    """Main entry point for the MCP server."""
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

    # Initialize and run the server
    server = LunoMCPServer()
    await server.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)

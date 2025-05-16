"""
Main entry point for the Luno MCP server.
"""

import asyncio
import logging
import sys
from src.luno_mcp_server.server import LunoMCPServer

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

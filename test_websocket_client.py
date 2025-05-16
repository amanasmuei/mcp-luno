#!/usr/bin/env python
"""
WebSocket test client for the Luno MCP server.

This script connects to the WebSocket server and sends a test request.
"""

import sys
import json
import asyncio
import websockets
import logging

# Configure logging with output to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


async def test_client(uri: str = "ws://localhost:8765"):
    """
    Connect to the WebSocket server and send a test request.

    Args:
        uri: The WebSocket URI to connect to.
    """
    logger.info(f"Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        logger.info("Connected to WebSocket server")

        # Prepare a test request - get market overview
        request = {
            "jsonrpc": "2.0",
            "method": "describe_capabilities",
            "params": {},
            "id": 1,
        }

        # Send the request
        request_json = json.dumps(request)
        logger.info(f"Sending request: {request_json}")
        await websocket.send(request_json)

        # Wait for the response
        logger.info("Waiting for response...")
        response = await websocket.recv()

        # Parse and log the response
        response_json = json.loads(response)
        logger.info(f"Received response: {json.dumps(response_json, indent=2)}")

        # If successful, try another request
        if "result" in response_json:
            # Send a second request - get crypto price
            price_request = {
                "jsonrpc": "2.0",
                "method": "get_crypto_price",
                "params": {"pair": "XBTZAR"},
                "id": 2,
            }

            # Send the request
            price_request_json = json.dumps(price_request)
            logger.info(f"Sending price request: {price_request_json}")
            await websocket.send(price_request_json)

            # Wait for the response
            logger.info("Waiting for price response...")
            price_response = await websocket.recv()

            # Parse and log the response
            price_response_json = json.loads(price_response)
            logger.info(
                f"Received price response: {json.dumps(price_response_json, indent=2)}"
            )


async def main():
    """Main entry point for the test client."""
    uri = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765"
    await test_client(uri)


if __name__ == "__main__":
    asyncio.run(main())

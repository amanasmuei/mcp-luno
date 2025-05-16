#!/usr/bin/env python
"""
Enhanced WebSocket client for the Luno MCP server.

This script demonstrates advanced features of multi-client connections to the MCP server:
1. Multiple simultaneous connections
2. Keep-alive functionality
3. Reconnection logic
4. Parallel requests
5. Command-line interface
"""

import sys
import os
import json
import asyncio
import random
import argparse
import logging
import websockets
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Available trading pairs on Luno
TRADING_PAIRS = ["XBTZAR", "ETHZAR", "XRPZAR", "LTCZAR", "BCHZAR", "BTCNGN", "ETHNGN"]


class EnhancedWebSocketClient:
    """Enhanced WebSocket client for the Luno MCP server."""

    def __init__(self, uri: str = "ws://localhost:8765", client_id: str = "client1"):
        """
        Initialize the client.

        Args:
            uri: The WebSocket URI to connect to.
            client_id: A unique identifier for this client.
        """
        self.uri = uri
        self.client_id = client_id
        self.websocket = None
        self.id_counter = 0
        self.disconnected = True
        self.capabilities = None

    def next_id(self) -> int:
        """Get the next request ID."""
        self.id_counter += 1
        return self.id_counter

    async def connect(self):
        """Connect to the WebSocket server."""
        if not self.disconnected:
            return

        try:
            logger.info(f"[{self.client_id}] Connecting to {self.uri}...")
            self.websocket = await websockets.connect(self.uri)
            self.disconnected = False
            logger.info(f"[{self.client_id}] Connected to WebSocket server")

            # Get server capabilities on connect
            await self.get_capabilities()
        except Exception as e:
            logger.error(f"[{self.client_id}] Connection error: {str(e)}")
            self.disconnected = True

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.disconnected:
            return

        try:
            await self.websocket.close()
            logger.info(f"[{self.client_id}] Disconnected from WebSocket server")
        except Exception as e:
            logger.error(f"[{self.client_id}] Disconnect error: {str(e)}")
        finally:
            self.disconnected = True

    async def send_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a request to the WebSocket server.

        Args:
            method: The MCP method to call.
            params: The parameters for the method.

        Returns:
            The response from the server, or None if an error occurred.
        """
        if self.disconnected:
            await self.connect()

        if self.disconnected:
            logger.error(f"[{self.client_id}] Cannot send request: not connected")
            return None

        request_id = self.next_id()

        # Prepare the request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id,
        }

        # Send the request
        request_json = json.dumps(request)
        try:
            logger.debug(f"[{self.client_id}] Sending request: {request_json}")
            await self.websocket.send(request_json)

            # Wait for the response
            response = await self.websocket.recv()

            # Parse the response
            response_json = json.loads(response)

            # Check for errors
            if "error" in response_json:
                logger.error(f"[{self.client_id}] Error: {response_json['error']}")

            return response_json
        except websockets.exceptions.ConnectionClosed:
            logger.error(f"[{self.client_id}] Connection closed during request")
            self.disconnected = True
            return None
        except Exception as e:
            logger.error(f"[{self.client_id}] Request error: {str(e)}")
            return None

    async def get_capabilities(self) -> Optional[Dict[str, Any]]:
        """Get the server capabilities."""
        response = await self.send_request("describe_capabilities")
        if response and "result" in response:
            self.capabilities = response["result"]
            logger.info(
                f"[{self.client_id}] Server capabilities: {json.dumps(self.capabilities, indent=2)}"
            )
            return self.capabilities
        return None

    async def get_crypto_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get the current price of a cryptocurrency pair.

        Args:
            pair: The trading pair to get the price for (e.g., "XBTZAR" for Bitcoin-ZAR)
        """
        response = await self.send_request("get_crypto_price", {"pair": pair})
        if response and "result" in response:
            return response["result"]
        return None

    async def keep_alive(self, interval: float = 30.0):
        """
        Keep the connection alive by sending periodic requests.

        Args:
            interval: The interval in seconds between keep-alive requests.
        """
        while True:
            try:
                await asyncio.sleep(interval)
                if self.disconnected:
                    await self.connect()
                    continue

                # Send a capabilities request as a keep-alive
                logger.info(f"[{self.client_id}] Sending keep-alive request")
                await self.get_capabilities()
            except Exception as e:
                logger.error(f"[{self.client_id}] Keep-alive error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def monitor_prices(self, pairs: List[str], interval: float = 5.0):
        """
        Monitor prices for multiple trading pairs.

        Args:
            pairs: The trading pairs to monitor.
            interval: The interval in seconds between price checks.
        """
        while True:
            try:
                for pair in pairs:
                    if self.disconnected:
                        await self.connect()

                    price = await self.get_crypto_price(pair)
                    if price:
                        timestamp = datetime.fromtimestamp(
                            price["timestamp"] / 1000
                        ).strftime("%H:%M:%S")
                        logger.info(
                            f"[{self.client_id}] {pair} @ {timestamp}: Ask: {price['ask']}, Bid: {price['bid']}, Last: {price['last_trade']}"
                        )

                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"[{self.client_id}] Price monitoring error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying


async def simulate_multiple_clients(client_count: int = 3, duration: int = 60):
    """
    Simulate multiple clients connecting to the server.

    Args:
        client_count: The number of clients to simulate.
        duration: The duration in seconds to run the simulation.
    """
    # Create clients
    clients = [
        EnhancedWebSocketClient(client_id=f"client{i+1}") for i in range(client_count)
    ]

    # Connect all clients
    for client in clients:
        await client.connect()

    # Create monitoring tasks for each client with different pairs
    monitoring_tasks = []
    for i, client in enumerate(clients):
        # Each client monitors different pairs
        pairs = random.sample(TRADING_PAIRS, min(3, len(TRADING_PAIRS)))
        task = asyncio.create_task(client.monitor_prices(pairs, interval=5.0 + i))
        monitoring_tasks.append(task)

    # Create keep-alive tasks
    keepalive_tasks = [
        asyncio.create_task(client.keep_alive(interval=15.0 + i * 5))
        for i, client in enumerate(clients)
    ]

    # Wait for the specified duration
    logger.info(f"Running {client_count} clients for {duration} seconds")
    await asyncio.sleep(duration)

    # Cancel all tasks
    for task in monitoring_tasks + keepalive_tasks:
        task.cancel()

    # Disconnect all clients
    for client in clients:
        await client.disconnect()

    logger.info("Simulation completed")


async def main():
    """Main entry point for the enhanced WebSocket client."""
    parser = argparse.ArgumentParser(
        description="Enhanced WebSocket client for Luno MCP server"
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="ws://localhost:8765",
        help="WebSocket URI to connect to",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "multi"],
        default="single",
        help="Mode to run the client in (single or multi)",
    )
    parser.add_argument(
        "--clients",
        type=int,
        default=3,
        help="Number of clients to simulate in multi mode",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in seconds to run the simulation",
    )
    parser.add_argument(
        "--pairs",
        type=str,
        default="XBTZAR,ETHZAR",
        help="Comma-separated list of trading pairs to monitor",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Interval in seconds between price checks",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    if args.mode == "multi":
        # Run multiple clients
        await simulate_multiple_clients(args.clients, args.duration)
    else:
        # Run a single client
        pairs = args.pairs.split(",")
        client = EnhancedWebSocketClient(args.uri)

        # Connect to the server
        await client.connect()

        # Start monitoring prices
        monitoring_task = asyncio.create_task(
            client.monitor_prices(pairs, args.interval)
        )

        # Start keep-alive task
        keepalive_task = asyncio.create_task(client.keep_alive(30.0))

        try:
            # Run for the specified duration
            await asyncio.sleep(args.duration)
        except asyncio.CancelledError:
            pass
        finally:
            # Cancel tasks
            monitoring_task.cancel()
            keepalive_task.cancel()

            # Disconnect
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

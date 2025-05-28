#!/usr/bin/env python
"""
Unified test client for the Luno MCP server.

This script supports testing both STDIO and WebSocket transports with various options.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import websockets
from subprocess import Popen, PIPE
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class MCPTestClient:
    """Unified test client for MCP server."""

    def __init__(self, transport="stdio", uri="ws://localhost:8765"):
        self.transport = transport
        self.uri = uri
        self.process = None
        self.websocket = None
        self.request_id = 0

    def next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def connect(self):
        """Connect to the MCP server."""
        if self.transport == "websocket":
            logger.info(f"Connecting to WebSocket server at {self.uri}")
            self.websocket = await websockets.connect(self.uri)
            logger.info("Connected to WebSocket server")
        else:
            logger.info("Starting STDIO MCP server process")
            self.process = Popen(
                ["python", "-m", "src.main", "--transport", "stdio"],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                bufsize=1,
            )

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.transport == "websocket" and self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket server")
        elif self.process:
            self.process.terminate()
            self.process.wait()
            logger.info("STDIO server process terminated")

    async def send_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.next_id(),
        }

        request_json = json.dumps(request)
        logger.info(f"Sending request: {request_json}")

        try:
            if self.transport == "websocket":
                await self.websocket.send(request_json)
                response = await self.websocket.recv()
            else:
                self.process.stdin.write(f"{request_json}\n")
                self.process.stdin.flush()
                response = self.process.stdout.readline().strip()

            response_obj = json.loads(response)
            logger.info(f"Received response: {response}")
            return response_obj

        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return None

    async def test_capabilities(self):
        """Test server capabilities."""
        logger.info("Testing server capabilities...")
        response = await self.send_request("describe_capabilities")

        if response and "result" in response:
            result = response["result"]
            print("\n✅ Server capabilities test passed!")
            print(f"  Name: {result['name']}")
            print(f"  Version: {result['version']}")
            print(f"  Description: {result['description']}")
            print("\n  Available methods:")
            for method in result["methods"]:
                print(f"    - {method}")
            return True
        else:
            print(f"\n❌ Server capabilities test failed: {response}")
            return False

    async def test_crypto_price(self, pair="XBTZAR"):
        """Test cryptocurrency price retrieval."""
        logger.info(f"Testing crypto price for {pair}...")
        response = await self.send_request("get_crypto_price", {"pair": pair})

        if response and "result" in response:
            result = response["result"]
            print(f"\n✅ Price test passed for {pair}!")
            print(f"  Ask: {result.get('ask')}")
            print(f"  Bid: {result.get('bid')}")
            print(f"  Last Trade: {result.get('last_trade')}")
            return True
        else:
            print(f"\n❌ Price test failed for {pair}: {response}")
            return False

    async def test_market_overview(self):
        """Test market overview."""
        logger.info("Testing market overview...")
        response = await self.send_request("get_market_overview")

        if response and "result" in response:
            result = response["result"]
            markets = result.get("markets", [])
            print(f"\n✅ Market overview test passed!")
            print(f"  Found {len(markets)} markets")
            if markets:
                print("  Sample markets:")
                for market in markets[:3]:  # Show first 3
                    print(f"    - {market}")
            return True
        else:
            print(f"\n❌ Market overview test failed: {response}")
            return False

    async def run_basic_tests(self):
        """Run basic functionality tests."""
        print("=== Running Basic MCP Server Tests ===")

        await self.connect()

        try:
            # Test 1: Server capabilities
            test1 = await self.test_capabilities()

            # Test 2: Crypto price (public endpoint)
            test2 = await self.test_crypto_price()

            # Test 3: Market overview (public endpoint)
            test3 = await self.test_market_overview()

            # Summary
            passed = sum([test1, test2, test3])
            total = 3

            print(f"\n=== Test Summary ===")
            print(f"Transport: {self.transport.upper()}")
            print(f"Passed: {passed}/{total} tests")

            if passed == total:
                print("🎉 All tests passed! Server is working correctly.")
            else:
                print("⚠️  Some tests failed. Check logs for details.")

        finally:
            await self.disconnect()

    async def monitor_prices(self, pairs=["XBTZAR", "ETHZAR"], duration=30):
        """Monitor cryptocurrency prices."""
        print(f"=== Monitoring Prices for {duration} seconds ===")

        await self.connect()

        try:
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < duration:
                for pair in pairs:
                    response = await self.send_request(
                        "get_crypto_price", {"pair": pair}
                    )

                    if response and "result" in response:
                        result = response["result"]
                        print(
                            f"{pair}: Ask={result.get('ask')}, Bid={result.get('bid')}"
                        )

                    await asyncio.sleep(1)  # Delay between pairs

                await asyncio.sleep(5)  # Wait before next round

        finally:
            await self.disconnect()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test client for Luno MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket"],
        default="stdio",
        help="Transport type to use",
    )
    parser.add_argument(
        "--uri",
        default="ws://localhost:8765",
        help="WebSocket URI (for websocket transport)",
    )
    parser.add_argument(
        "--mode",
        choices=["test", "monitor"],
        default="test",
        help="Mode: run basic tests or monitor prices",
    )
    parser.add_argument(
        "--pairs",
        default="XBTZAR,ETHZAR",
        help="Comma-separated trading pairs to monitor",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration for monitoring mode (seconds)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Create client
    client = MCPTestClient(transport=args.transport, uri=args.uri)

    if args.mode == "monitor":
        pairs = args.pairs.split(",")
        await client.monitor_prices(pairs, args.duration)
    else:
        await client.run_basic_tests()


if __name__ == "__main__":
    asyncio.run(main())

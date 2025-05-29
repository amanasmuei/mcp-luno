#!/usr/bin/env python
"""
Updated test client for the Luno MCP server using FastMCP.

This script supports testing both STDIO and HTTP-based transports with various options.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, Any, Optional
from fastmcp import Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class FastMCPTestClient:
    """Test client for FastMCP Luno server."""

    def __init__(self, transport="stdio", host="localhost", port=8000):
        self.transport = transport
        self.host = host
        self.port = port
        self.client = None

    async def connect(self):
        """Connect to the FastMCP server."""
        if self.transport == "stdio":
            logger.info("Creating STDIO client for FastMCP server")
            # For STDIO, we need to run the server as a subprocess
            self.client = Client("python -m src.main --transport stdio")
        elif self.transport == "streamable-http":
            logger.info(f"Creating Streamable HTTP client for {self.host}:{self.port}")
            self.client = Client(f"http://{self.host}:{self.port}")
        elif self.transport == "sse":
            logger.info(f"Creating SSE client for {self.host}:{self.port}")
            self.client = Client(f"http://{self.host}:{self.port}/sse")
        else:
            raise ValueError(f"Unsupported transport: {self.transport}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self):
        """List available tools."""
        return await self.client.list_tools()

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Call a tool."""
        return await self.client.call_tool(name, arguments)

    async def test_server_info(self):
        """Test server basic information."""
        logger.info("Testing server tools...")
        try:
            tools = await self.list_tools()
            print(f"\n✅ Server connected successfully!")
            print(f"  Available tools: {len(tools.tools)}")
            print("\n  Tool list:")
            for tool in tools.tools:
                print(f"    - {tool.name}: {tool.description}")
            return True
        except Exception as e:
            print(f"\n❌ Server connection failed: {e}")
            return False

    async def test_crypto_price(self, pair="XBTZAR"):
        """Test cryptocurrency price retrieval."""
        logger.info(f"Testing crypto price for {pair}...")
        try:
            result = await self.call_tool("get_crypto_price", {"pair": pair})
            if result and len(result) > 0:
                response_text = result[0].text
                response = json.loads(response_text)

                if "error" in response:
                    print(
                        f"\n⚠️  Price test returned error for {pair}: {response['error']}"
                    )
                    return False

                print(f"\n✅ Price test passed for {pair}!")
                print(f"  Ask: {response.get('ask')}")
                print(f"  Bid: {response.get('bid')}")
                print(f"  Last Trade: {response.get('last_trade')}")
                print(f"  Volume (24h): {response.get('rolling_24_hour_volume')}")
                return True
        except Exception as e:
            print(f"\n❌ Price test failed for {pair}: {e}")
            return False

    async def test_market_overview(self):
        """Test market overview."""
        logger.info("Testing market overview...")
        try:
            result = await self.call_tool("get_market_overview", {})
            if result and len(result) > 0:
                response_text = result[0].text
                response = json.loads(response_text)

                if "error" in response:
                    print(
                        f"\n⚠️  Market overview test returned error: {response['error']}"
                    )
                    return False

                markets = response.get("markets", [])
                print(f"\n✅ Market overview test passed!")
                print(f"  Found {len(markets)} markets")
                if markets:
                    print("  Sample markets:")
                    for market in markets[:3]:  # Show first 3
                        if isinstance(market, dict):
                            print(f"    - {market.get('pair', 'Unknown')}")
                        else:
                            print(f"    - {market}")
                return True
        except Exception as e:
            print(f"\n❌ Market overview test failed: {e}")
            return False

    async def test_account_balance(self):
        """Test account balance (requires auth)."""
        logger.info("Testing account balance...")
        try:
            result = await self.call_tool("get_account_balance", {})
            if result and len(result) > 0:
                response_text = result[0].text
                response = json.loads(response_text)

                if "error" in response:
                    if (
                        "authentication" in response["error"].lower()
                        or "credentials" in response["error"].lower()
                    ):
                        print(
                            f"\n⚠️  Account balance test skipped (no auth): {response['error']}"
                        )
                        return True  # This is expected without credentials
                    print(
                        f"\n⚠️  Account balance test returned error: {response['error']}"
                    )
                    return False

                print(f"\n✅ Account balance test passed!")
                balances = response.get("balance", [])
                print(f"  Found {len(balances)} account balances")
                for balance in balances[:3]:  # Show first 3
                    asset = balance.get("asset", "Unknown")
                    amount = balance.get("balance", "0")
                    print(f"    - {asset}: {amount}")
                return True
        except Exception as e:
            print(f"\n❌ Account balance test failed: {e}")
            return False

    async def test_fees(self, pair="XBTZAR"):
        """Test fees information."""
        logger.info(f"Testing fees for {pair}...")
        try:
            result = await self.call_tool("get_fees", {"pair": pair})
            if result and len(result) > 0:
                response_text = result[0].text
                response = json.loads(response_text)

                if "error" in response:
                    if (
                        "authentication" in response["error"].lower()
                        or "credentials" in response["error"].lower()
                    ):
                        print(f"\n⚠️  Fees test skipped (no auth): {response['error']}")
                        return True  # This is expected without credentials
                    print(
                        f"\n⚠️  Fees test returned error for {pair}: {response['error']}"
                    )
                    return False

                print(f"\n✅ Fees test passed for {pair}!")
                print(f"  Maker fee: {response.get('maker_fee')}")
                print(f"  Taker fee: {response.get('taker_fee')}")
                print(f"  30-day volume: {response.get('thirty_day_volume')}")
                return True
        except Exception as e:
            print(f"\n❌ Fees test failed for {pair}: {e}")
            return False

    async def run_basic_tests(self):
        """Run basic functionality tests."""
        print("=== Running FastMCP Server Tests ===")

        test_results = []

        # Test 1: Server info and tools
        test_results.append(await self.test_server_info())

        # Test 2: Crypto price (public endpoint)
        test_results.append(await self.test_crypto_price())

        # Test 3: Market overview (public endpoint)
        test_results.append(await self.test_market_overview())

        # Test 4: Account balance (private endpoint - may fail without auth)
        test_results.append(await self.test_account_balance())

        # Test 5: Fees (private endpoint - may fail without auth)
        test_results.append(await self.test_fees())

        # Summary
        passed = sum(test_results)
        total = len(test_results)

        print(f"\n=== Test Summary ===")
        print(f"Transport: {self.transport.upper()}")
        print(f"Passed: {passed}/{total} tests")

        if passed == total:
            print("🎉 All tests passed! FastMCP server is working correctly.")
        else:
            print("⚠️  Some tests failed. Check logs for details.")
            print(
                "   Note: Private endpoint failures are expected without API credentials."
            )

        return passed == total

    async def monitor_prices(self, pairs=["XBTZAR", "ETHZAR"], duration=30):
        """Monitor cryptocurrency prices."""
        print(f"=== Monitoring Prices for {duration} seconds ===")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            for pair in pairs:
                try:
                    result = await self.call_tool("get_crypto_price", {"pair": pair})
                    if result and len(result) > 0:
                        response_text = result[0].text
                        response = json.loads(response_text)

                        if "error" not in response:
                            print(
                                f"{pair}: Ask={response.get('ask')}, Bid={response.get('bid')}"
                            )
                        else:
                            print(f"{pair}: Error - {response['error']}")
                except Exception as e:
                    print(f"{pair}: Exception - {e}")

                await asyncio.sleep(1)  # Delay between pairs

            await asyncio.sleep(5)  # Wait before next round


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FastMCP test client for Luno MCP server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport type to use",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP-based transports",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP-based transports",
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
    async with FastMCPTestClient(
        transport=args.transport, host=args.host, port=args.port
    ) as client:
        if args.mode == "monitor":
            pairs = args.pairs.split(",")
            await client.monitor_prices(pairs, args.duration)
        else:
            await client.run_basic_tests()


if __name__ == "__main__":
    asyncio.run(main())

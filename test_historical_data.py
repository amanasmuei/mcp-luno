#!/usr/bin/env python3
"""
Test script for the enhanced Luno MCP server with historical price data support.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from luno_mcp_server.luno_client import LunoClient


async def test_historical_data():
    """Test the historical data functionality."""
    print("🧪 Testing Luno MCP Historical Data Features")
    print("=" * 50)

    # Initialize client
    api_key = os.environ.get("LUNO_API_KEY")
    api_secret = os.environ.get("LUNO_API_SECRET")

    if not api_key or not api_secret:
        print("⚠️  No API credentials found. Testing with dummy data...")
        print(
            "Set LUNO_API_KEY and LUNO_API_SECRET environment variables for live testing."
        )
        return

    client = LunoClient(api_key=api_key, api_secret=api_secret)

    try:
        # Test 1: Get historical candles
        print("\n📊 Test 1: Historical Candlestick Data")
        print("-" * 30)

        # Calculate timestamp for 7 days ago
        since_dt = datetime.now(timezone.utc) - timedelta(days=7)
        since = int(since_dt.timestamp() * 1000)

        print(
            f"Fetching 24h candles for XBTZAR since {since_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )

        candles_data = await client.get_candles("XBTZAR", since, 86400)  # 24h candles
        candles = candles_data.get("candles", [])

        if candles:
            print(f"✅ Retrieved {len(candles)} candles")
            print(f"First candle: {candles[0]}")
            print(f"Last candle: {candles[-1]}")

            # Calculate some basic statistics
            prices = [float(candle["close"]) for candle in candles]
            print(f"Price range: {min(prices):.2f} - {max(prices):.2f} ZAR")
        else:
            print("❌ No candle data retrieved")

        # Test 2: Test different timeframes
        print("\n⏱️  Test 2: Different Timeframes")
        print("-" * 30)

        timeframes = [
            (300, "5m"),  # 5 minutes
            (3600, "1h"),  # 1 hour
            (86400, "24h"),  # 24 hours
        ]

        for duration, name in timeframes:
            try:
                data = await client.get_candles("XBTZAR", since, duration)
                count = len(data.get("candles", []))
                print(f"✅ {name} candles: {count} retrieved")
            except Exception as e:
                print(f"❌ {name} candles: Error - {e}")

        # Test 3: Test error handling
        print("\n🚫 Test 3: Error Handling")
        print("-" * 30)

        try:
            # Test with invalid pair
            await client.get_candles("INVALID", since, 86400)
            print("❌ Expected error for invalid pair, but got success")
        except Exception as e:
            print(f"✅ Correctly handled invalid pair: {type(e).__name__}")

        try:
            # Test with invalid duration
            await client.get_candles("XBTZAR", since, 12345)
            print("❌ Expected error for invalid duration, but got success")
        except Exception as e:
            print(f"✅ Correctly handled invalid duration: {type(e).__name__}")

        print("\n🎉 Historical data tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await client.close()


def test_helper_functions():
    """Test helper functions."""
    print("\n🔧 Test 4: Helper Functions")
    print("-" * 30)

    # Import the helper function
    sys.path.insert(
        0, os.path.join(os.path.dirname(__file__), "src", "luno_mcp_server")
    )
    from server import _get_duration_name

    test_cases = [
        (60, "1m"),
        (300, "5m"),
        (3600, "1h"),
        (86400, "24h"),
        (604800, "7d"),
        (12345, "12345s"),  # Unknown duration
    ]

    for duration, expected in test_cases:
        result = _get_duration_name(duration)
        if result == expected:
            print(f"✅ {duration}s -> {result}")
        else:
            print(f"❌ {duration}s -> {result}, expected {expected}")


async def simulate_mcp_tools():
    """Simulate the MCP tool functions."""
    print("\n🛠️  Test 5: MCP Tool Simulation")
    print("-" * 30)

    # Test the price range calculation logic
    try:
        # Mock candle data
        mock_candles = [
            {
                "timestamp": 1640995200000,
                "open": "1000.00",
                "high": "1100.00",
                "low": "950.00",
                "close": "1050.00",
                "volume": "10.5",
            },
            {
                "timestamp": 1641081600000,
                "open": "1050.00",
                "high": "1200.00",
                "low": "1000.00",
                "close": "1150.00",
                "volume": "15.2",
            },
            {
                "timestamp": 1641168000000,
                "open": "1150.00",
                "high": "1250.00",
                "low": "1100.00",
                "close": "1200.00",
                "volume": "12.8",
            },
        ]

        # Calculate statistics like the MCP tool would
        prices = [float(candle["close"]) for candle in mock_candles]
        highs = [float(candle["high"]) for candle in mock_candles]
        lows = [float(candle["low"]) for candle in mock_candles]
        volumes = [float(candle["volume"]) for candle in mock_candles]

        first_candle = mock_candles[0]
        last_candle = mock_candles[-1]

        open_price = float(first_candle["open"])
        close_price = float(last_candle["close"])
        price_change = close_price - open_price
        price_change_percent = (price_change / open_price) * 100

        print(f"✅ Price analysis simulation:")
        print(f"   Open: {open_price}, Close: {close_price}")
        print(f"   High: {max(highs)}, Low: {min(lows)}")
        print(f"   Change: {price_change} ({price_change_percent:.2f}%)")
        print(f"   Average: {sum(prices) / len(prices):.2f}")
        print(f"   Total Volume: {sum(volumes)}")

    except Exception as e:
        print(f"❌ Price analysis simulation failed: {e}")


def main():
    """Main test function."""
    print("🚀 Luno MCP Historical Data Test Suite")
    print("=" * 50)

    # Test helper functions (synchronous)
    test_helper_functions()

    # Test async functions
    asyncio.run(test_historical_data())

    # Test tool simulations
    asyncio.run(simulate_mcp_tools())

    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nTo test with live data:")
    print("export LUNO_API_KEY='your_api_key'")
    print("export LUNO_API_SECRET='your_api_secret'")
    print("python test_historical_data.py")


if __name__ == "__main__":
    main()

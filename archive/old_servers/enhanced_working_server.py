#!/usr/bin/env python3
"""
Enhanced Working Luno MCP Server - Supports all trading pairs with real API integration.

This server supports any Luno trading pair and provides real data when API credentials are available.
"""

import os
import sys
import json
import asyncio
import logging

# Setup logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def send_response(response):
    """Send a response to stdout and flush."""
    print(json.dumps(response))
    sys.stdout.flush()
    logger.info(
        f"Sent response: {response.get('id')} - {response.get('result', {}).get('type', 'unknown')}"
    )


async def get_real_price(pair):
    """Get real price from Luno API."""
    try:
        # Import httpx only when needed
        import httpx

        api_key = os.environ.get("LUNO_API_KEY")
        api_secret = os.environ.get("LUNO_API_SECRET")

        async with httpx.AsyncClient() as client:
            auth = (api_key, api_secret) if api_key and api_secret else None

            response = await client.get(
                f"https://api.luno.com/api/1/ticker",
                params={"pair": pair},
                auth=auth,
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data, "pair": pair}
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "pair": pair,
                }

    except ImportError:
        return {
            "success": False,
            "error": "httpx not available - install with: pip3 install httpx",
            "pair": pair,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "pair": pair}


async def get_real_balances():
    """Get real account balances from Luno API."""
    try:
        import httpx

        api_key = os.environ.get("LUNO_API_KEY")
        api_secret = os.environ.get("LUNO_API_SECRET")

        if not (api_key and api_secret):
            return {"success": False, "error": "API credentials required"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.luno.com/api/1/balance",
                auth=(api_key, api_secret),
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                }

    except ImportError:
        return {
            "success": False,
            "error": "httpx not available - install with: pip3 install httpx",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_initialize(request_id):
    """Handle the initialize request."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "luno-mcp-server", "version": "0.2.0"},
        },
    }
    send_response(response)


def handle_tools_list(request_id):
    """Handle the tools/list request."""
    # Check if we have API credentials
    has_credentials = bool(
        os.environ.get("LUNO_API_KEY") and os.environ.get("LUNO_API_SECRET")
    )

    tools = [
        {
            "name": "get_crypto_price",
            "description": "Get current price for any cryptocurrency trading pair (e.g., XBTZAR, ETHZAR, XBTEUR, ETHEUR, ADAZAR, etc.)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair like XBTZAR, ETHZAR, XBTEUR, ETHEUR, ADAZAR, SOLGBP, etc.",
                    }
                },
                "required": ["pair"],
            },
        },
        {
            "name": "get_market_overview",
            "description": "Get overview of all available trading pairs and markets",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]

    if has_credentials:
        tools.append(
            {
                "name": "get_account_balance",
                "description": "Get real account balances for all currencies",
                "inputSchema": {"type": "object", "properties": {}},
            }
        )

    response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
    send_response(response)


def handle_tools_call(request_id, params):
    """Handle the tools/call request."""
    name = params.get("name", "")
    arguments = params.get("arguments", {})

    try:
        if name == "get_crypto_price":
            # Get the trading pair from arguments
            pair = arguments.get("pair", "").upper()

            if not pair:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "❌ Please specify a trading pair. Examples:\n• XBTZAR (Bitcoin to South African Rand)\n• ETHZAR (Ethereum to ZAR)\n• XBTEUR (Bitcoin to Euro)\n• ETHEUR (Ethereum to Euro)\n• ADAZAR (Cardano to ZAR)",
                            }
                        ]
                    },
                }
                send_response(response)
                return

            # Run async price fetch
            async def fetch_and_respond():
                price_result = await get_real_price(pair)

                if price_result["success"]:
                    data = price_result["data"]

                    # Extract currency info from pair
                    if len(pair) == 6:
                        base_currency = pair[:3]
                        quote_currency = pair[3:]
                    else:
                        base_currency = "Unknown"
                        quote_currency = "Unknown"

                    # Format the response nicely
                    ask_price = data.get("ask", "N/A")
                    bid_price = data.get("bid", "N/A")
                    last_trade = data.get("last_trade", "N/A")
                    volume = data.get("rolling_24_hour_volume", "N/A")
                    timestamp = data.get("timestamp", "N/A")

                    # Determine currency symbol
                    currency_symbols = {"ZAR": "R", "EUR": "€", "GBP": "£", "USD": "$"}
                    symbol = currency_symbols.get(quote_currency, "")

                    text_response = f"""💰 **{base_currency}/{quote_currency} Price Information**

**Current Prices:**
• Ask (Sell): {symbol}{ask_price}
• Bid (Buy): {symbol}{bid_price}  
• Last Trade: {symbol}{last_trade}

**Market Data:**
• 24h Volume: {volume} {base_currency}
• Timestamp: {timestamp}
• Pair: {pair}

**Real-time data from Luno API** ✅"""

                else:
                    # Handle API errors gracefully
                    error_msg = price_result["error"]

                    # Provide helpful suggestions for common errors
                    suggestions = ""
                    if "404" in error_msg or "not found" in error_msg.lower():
                        suggestions = "\n\n**Available pairs include:**\n• XBTZAR, ETHZAR, ADAZAR (ZAR pairs)\n• XBTEUR, ETHEUR (EUR pairs)\n• XBTGBP, ETHGBP (GBP pairs)"
                    elif "timeout" in error_msg.lower():
                        suggestions = "\n\n**Try again** - API request timed out"

                    text_response = f"""❌ **Error getting price for {pair}**

Error: {error_msg}{suggestions}

**Popular trading pairs:**
• Bitcoin: XBTZAR, XBTEUR, XBTGBP
• Ethereum: ETHZAR, ETHEUR, ETHGBP  
• Cardano: ADAZAR
• Solana: SOLGBP"""

                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": text_response}]},
                }
                send_response(response)

            # Run the async function
            asyncio.create_task(fetch_and_respond())
            return

        elif name == "get_market_overview":
            # Provide information about available markets
            text_response = """🏪 **Luno Trading Markets Overview**

**Popular Trading Pairs:**

**🇿🇦 South African Rand (ZAR) Pairs:**
• XBTZAR - Bitcoin to ZAR
• ETHZAR - Ethereum to ZAR  
• ADAZAR - Cardano to ZAR

**🇪🇺 Euro (EUR) Pairs:**
• XBTEUR - Bitcoin to EUR
• ETHEUR - Ethereum to EUR

**🇬🇧 British Pound (GBP) Pairs:**
• XBTGBP - Bitcoin to GBP
• ETHGBP - Ethereum to GBP
• SOLGBP - Solana to GBP

**💡 Usage Examples:**
• "Get crypto price for ETHZAR"
• "What's the Bitcoin price in EUR?"
• "Show me ADAZAR price"

**Note:** Use the `get_crypto_price` tool with any pair above to get real-time pricing data."""

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": text_response}]},
            }
            send_response(response)

        elif name == "get_account_balance":
            # Get real account balances
            async def fetch_balances():
                balance_result = await get_real_balances()

                if balance_result["success"]:
                    data = balance_result["data"]
                    balances = data.get("balance", [])

                    if balances:
                        text_response = "💰 **Account Balances:**\n\n"

                        for balance in balances:
                            asset = balance.get("asset", "Unknown")
                            available = balance.get("balance", "0")
                            reserved = balance.get("reserved", "0")

                            # Format currency display
                            if asset == "ZAR":
                                text_response += f"• **{asset}**: R{available} (Reserved: R{reserved})\n"
                            elif asset in ["EUR", "GBP", "USD"]:
                                symbols = {"EUR": "€", "GBP": "£", "USD": "$"}
                                symbol = symbols[asset]
                                text_response += f"• **{asset}**: {symbol}{available} (Reserved: {symbol}{reserved})\n"
                            else:
                                text_response += f"• **{asset}**: {available} (Reserved: {reserved})\n"

                        text_response += (
                            "\n**Real-time data from your Luno account** ✅"
                        )
                    else:
                        text_response = "💰 **Account Balances:**\n\nNo balances found or account may be empty."

                else:
                    text_response = f"❌ **Error getting account balances:**\n\n{balance_result['error']}\n\nPlease check your API credentials."

                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": text_response}]},
                }
                send_response(response)

            asyncio.create_task(fetch_balances())
            return

        else:
            # Unknown tool
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"},
            }
            send_response(response)

    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }
        send_response(response)


def handle_request(line):
    """Handle a single request line."""
    try:
        request = json.loads(line)
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        logger.info(f"Received request: {method} (ID: {request_id})")

        # Ensure we have a valid request ID
        if request_id is None:
            logger.warning("Request missing ID, using 0")
            request_id = 0

        if method == "initialize":
            handle_initialize(request_id)

        elif method == "initialized":
            # This is a notification - no response needed
            logger.info("Client initialized notification received")

        elif method == "tools/list":
            handle_tools_list(request_id)

        elif method == "tools/call":
            handle_tools_call(request_id, params)

        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
            send_response(response)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        # Send parse error
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
        }
        send_response(response)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }
        send_response(response)


def main():
    """Main server loop."""
    logger.info("Starting Enhanced Luno MCP Server")

    # Log credential and dependency status
    has_credentials = bool(
        os.environ.get("LUNO_API_KEY") and os.environ.get("LUNO_API_SECRET")
    )

    try:
        import httpx

        has_httpx = True
    except ImportError:
        has_httpx = False

    if has_credentials and has_httpx:
        logger.info(
            "✅ API credentials + httpx available - full real-time features enabled"
        )
    elif has_credentials:
        logger.info(
            "⚠️  API credentials available but httpx missing - install with: pip3 install httpx"
        )
    elif has_httpx:
        logger.info(
            "⚠️  httpx available but no API credentials - limited to demo responses"
        )
    else:
        logger.info("⚠️  No API credentials or httpx - demo mode only")

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if line:
                handle_request(line)

    except (EOFError, KeyboardInterrupt):
        logger.info("Server shutting down")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

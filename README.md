# 🚀 Luno MCP Server - FastMCP 2.0

A modern Model Context Protocol (MCP) server for the Luno cryptocurrency exchange, built with FastMCP 2.0 and Python 3.12.

## ✅ Quick Start

### 1. Install Dependencies

```bash
# Activate the virtual environment
source venv/bin/activate

# Dependencies are already installed:
# - fastmcp 2.5.1
# - httpx
# - pydantic
# - python-dotenv
```

### 2. Configure Claude Desktop

Add this to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "luno": {
      "command": "/Users/aman-asmuei/Documents/mcp/mcp-luno/venv/bin/python",
      "args": [
        "/Users/aman-asmuei/Documents/mcp/mcp-luno/src/luno_mcp_server/server.py"
      ],
      "cwd": "/Users/aman-asmuei/Documents/mcp/mcp-luno",
      "env": {
        "LUNO_API_KEY": "your_api_key_here",
        "LUNO_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

### 3. Test

Restart Claude Desktop and ask:
- **"What's the Bitcoin price in EUR?"**
- **"Get ETHZAR price"**
- **"Show me my account balance"**
- **"Get historical prices for XBTZAR over the last 7 days"**
- **"Show me Bitcoin price range analysis for the past 30 days"**

## 🛠️ Available Tools

### Public Tools (No API credentials required)
- `get_crypto_price` - Real-time prices for any trading pair
- `get_market_overview` - Market data and available pairs

### Historical Data Tools (API credentials required)
- `get_historical_prices` - OHLC candlestick data for any trading pair
- `get_price_range` - Price analysis over specified time periods (1-30 days)

### Private Tools (API credentials required)
- `get_account_balance` - Account balances
- `place_order` - Place buy/sell orders
- `cancel_order` - Cancel orders
- `get_order_status` - Check order status
- `get_transaction_history` - Transaction history
- `get_fees` - Trading fees

## 📈 Historical Price Data Features

### Candlestick Data (`get_historical_prices`)
- **Timeframes:** 1m, 5m, 15m, 30m, 1h, 3h, 4h, 8h, 24h, 3d, 7d
- **Data:** OHLC (Open, High, Low, Close) + Volume
- **Limit:** Up to 1000 candles per request
- **Format:** Standard candlestick data with timestamps

### Price Range Analysis (`get_price_range`)
- **Period:** 1-30 days of historical data
- **Statistics:** High, Low, Open, Close, Average prices
- **Metrics:** Price change, percentage change, total volume
- **Convenience:** Automatic daily candle aggregation

## 🌍 Supported Trading Pairs

- **ZAR (South Africa):** XBTZAR, ETHZAR, ADAZAR
- **EUR (Europe):** XBTEUR, ETHEUR
- **GBP (UK):** XBTGBP, ETHGBP, SOLGBP
- **USD (US):** XBTUSD, ETHUSD
- **And more!**

## 🏗️ Project Structure

```
luno-mcp/
├── src/
│   ├── luno_mcp/              # Modern FastMCP 2.0 implementation
│   │   ├── server.py          # Main server with all tools
│   │   ├── client.py          # Luno API client
│   │   ├── config.py          # Configuration management
│   │   └── tools/             # Modular tool organization
│   ├── luno_mcp_server/       # Working FastMCP server (CURRENT)
│   │   ├── server.py          # ← Currently used by Claude Desktop
│   │   └── luno_client.py     # Luno API client
│   └── main.py                # Alternative entry point
├── tests/                     # Test suite
├── docs/                      # Documentation
├── archive/                   # Old implementations
├── venv/                      # Python 3.12 virtual environment
└── README.md                  # This file
```

## 🔧 Technical Details

- **Python:** 3.12.10 (in virtual environment)
- **Framework:** FastMCP 2.5.1
- **API Client:** httpx for async HTTP requests
- **Transport:** STDIO (JSON-RPC 2.0)
- **Architecture:** Async/await with proper error handling

## 📚 Documentation

- [`docs/PYTHON_UPGRADE_GUIDE.md`](docs/PYTHON_UPGRADE_GUIDE.md) - Python upgrade process
- [`docs/MIGRATION.md`](docs/MIGRATION.md) - Migration from old versions
- [`docs/CLAUDE_DESKTOP_SETUP.md`](docs/CLAUDE_DESKTOP_SETUP.md) - Detailed setup guide

## 🔒 Security

- API credentials stored as environment variables
- All communications use HTTPS
- Virtual environment isolation
- No credentials logged or exposed

## 🚨 Troubleshooting

### Common Issues

1. **Import errors:** Make sure you're using the virtual environment
2. **API errors:** Check your Luno API credentials
3. **Connection issues:** Verify internet connectivity

### Get Help

1. Check the logs in Claude Desktop
2. Test the server directly: `python src/luno_mcp_server/server.py`
3. Verify dependencies: `pip list | grep fastmcp`

## 💖 Support This Project

If this Luno MCP server has been helpful for your cryptocurrency trading and analysis, consider supporting its development!

### ☕ Support This Project

[![GitHub Sponsors](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA)](https://github.com/sponsors/amanasmuei)

**🌍 Global donation options that work worldwide:**
- 💖 **GitHub Sponsors:** [github.com/sponsors/amanasmuei](https://github.com/sponsors/amanasmuei) *(Monthly/one-time)*
- 💳 **PayPal.me:** [paypal.me/amanasmuei](https://paypal.me/amanasmuei) *(Direct payments)*
- ⭐ **Star this repo** on GitHub
- 🐛 **Report issues** and contribute improvements
- 📢 **Share** with other crypto traders

### 🪙 Crypto Donations
- **Bitcoin (BTC):** `3CPb1HP6Gfpx3MZFdrm4nhoHk4VbX2eZRj`
- **Ethereum (ETH):** `0x54dC4eDf6c940C52A1434824634d8cE8629767b3`
- **Luno Trading:** Use this MCP server to trade! 📈

*Your support helps maintain and improve this free, open-source trading tool! 🚀*

---

## 🎉 Success!

You should now have a fully working Luno MCP server with:
- ✅ Real-time cryptocurrency prices
- ✅ **Historical price data and candlestick charts**
- ✅ **Price range analysis and statistics**
- ✅ Multi-currency support (ZAR, EUR, GBP, USD)
- ✅ Account management tools
- ✅ Trading capabilities
- ✅ FastMCP 2.0 architecture

**Ask Claude: "What's the Bitcoin price in EUR?" or "Show me XBTZAR price history for the past week" to test!**

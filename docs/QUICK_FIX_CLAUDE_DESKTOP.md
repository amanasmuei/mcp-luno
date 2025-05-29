# Quick Fix for Claude Desktop Connection Issues

Based on the error logs, here are the immediate solutions to get the Luno MCP server working with Claude Desktop:

## 🚨 Immediate Solution

Replace your `claude_desktop_config.json` with this working configuration:

### ✅ Standalone Server (No Dependencies Required)
```json
{
  "mcpServers": {
    "luno": {
      "command": "python3",
      "args": [
        "/Users/aman-asmuei/Documents/mcp/mcp-luno/src/standalone_server.py"
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

### Alternative: Install Dependencies First
If you want to use the advanced features, install dependencies:
```bash
pip3 install httpx
```

Then use this config:
```json
{
  "mcpServers": {
    "luno": {
      "command": "python3",
      "args": [
        "/Users/aman-asmuei/Documents/mcp/mcp-luno/src/main_legacy.py"
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

## 📋 Steps to Fix

1. **Locate your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Replace the content** with one of the configurations above

3. **Add your API credentials** (replace `your_api_key_here` and `your_api_secret_here`)

4. **Restart Claude Desktop** completely:
   - Quit Claude Desktop
   - Start it again

## 🔍 What Was Wrong

The errors show:
1. **Missing FastMCP dependency** - The new version requires `fastmcp` package
2. **Method 'initialize' not found** - Server protocol mismatch
3. **Module not found errors** - Import path issues

## ✅ Working Features

With the working configuration, you'll have access to:

**Public Tools (no API key needed):**
- `get_crypto_price` - Get crypto prices
- `get_market_overview` - Market data
- `get_orderbook` - Order book
- `get_recent_trades` - Trade history
- `get_all_tickers` - All tickers

**Private Tools (API key required):**
- `get_account_balance` - Account balances
- `place_order` - Place trades
- `cancel_order` - Cancel orders
- `get_order_status` - Order status
- `get_transaction_history` - Transaction history
- And more...

## 🚀 Test It Works

After restarting Claude Desktop, test with:
- "What's the current Bitcoin price in ZAR?"
- "Show me the Ethereum order book"
- "Get my account balance" (if you have API credentials)

## 🔧 For the New FastMCP Version

If you want to use the new refactored version later:

1. **Install dependencies:**
```bash
cd /Users/aman-asmuei/Documents/mcp/mcp-luno
pip3 install fastmcp>=2.0.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 httpx>=0.24.0 python-dotenv>=1.0.0
```

2. **Then use this config:**
```json
{
  "mcpServers": {
    "luno": {
      "command": "python3",
      "args": [
        "/Users/aman-asmuei/Documents/mcp/mcp-luno/src/main.py",
        "--transport",
        "stdio"
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

This should get you up and running immediately! 🎉
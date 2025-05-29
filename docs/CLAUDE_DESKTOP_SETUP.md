# Setting Up Luno MCP Server with Claude Desktop

This guide walks you through setting up the Luno MCP server to work with Claude Desktop, with multiple options depending on your setup.

## 📋 Prerequisites

1. **Claude Desktop App** installed on your system
2. **Python 3.9+** installed (check with `python3 --version`)
3. **Luno API credentials** (optional, for private endpoints)

## 🚀 Quick Start (Recommended)

The easiest way to get started is to use the existing working server:

### Option A: Use Existing Working Server

```json
{
  "mcpServers": {
    "luno": {
      "command": "python3",
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

### Option B: Use Adaptive Legacy Server

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

## 🔧 Step 1: Install Dependencies (Optional for New Version)

If you want to use the new FastMCP 2.0 version:

```bash
# Navigate to the project directory
cd /Users/aman-asmuei/Documents/mcp/mcp-luno

# Install required dependencies
pip3 install fastmcp>=2.0.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 httpx>=0.24.0 python-dotenv>=1.0.0

# Or install all at once
pip3 install -r requirements.txt
```

## 🔑 Step 2: Configure API Credentials (Optional)

If you want to use private endpoints (trading, account management):

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

Add your Luno API credentials:
```env
LUNO_API_KEY=your_actual_api_key_here
LUNO_API_SECRET=your_actual_api_secret_here
```

**Note:** You can skip this step if you only want to use public market data endpoints.

## 📱 Step 3: Find Claude Desktop Config File

The configuration file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

## ⚙️ Step 4: Configure Claude Desktop

### Option A: With API Credentials (Full Functionality)

Add this to your `claude_desktop_config.json`:

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
      "env": {
        "LUNO_API_KEY": "your_actual_api_key_here",
        "LUNO_API_SECRET": "your_actual_api_secret_here",
        "LUNO_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Option B: Without API Credentials (Public Data Only)

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
      "env": {
        "LUNO_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Option C: Using .env File (Recommended)

If you configured the `.env` file in Step 2:

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
      "cwd": "/Users/aman-asmuei/Documents/mcp/mcp-luno"
    }
  }
}
```

## 🧪 Step 5: Test the Setup

1. **Test the server manually** first:
```bash
cd /Users/aman-asmuei/Documents/mcp/mcp-luno
python3 src/main.py --transport stdio --log-level DEBUG
```

If it starts without errors, press `Ctrl+C` to stop.

2. **Restart Claude Desktop** completely:
   - Quit Claude Desktop
   - Start it again

3. **Check if the server is loaded**:
   - Open Claude Desktop
   - Start a new conversation
   - Look for the Luno MCP server in the available tools

## 🎯 Step 6: Verify Tools Are Available

In Claude Desktop, you should now have access to these tools:

### **Public Tools (Available without API credentials):**
- `get_crypto_price` - Get current price for a trading pair
- `get_market_overview` - Get overview of all markets
- `get_orderbook` - Get order book data
- `get_recent_trades` - Get recent trades
- `get_all_tickers` - Get all ticker information
- `check_api_health` - Check API connectivity

### **Private Tools (Require API credentials):**
- `get_account_balance` - Get account balances
- `get_accounts` - Get account information
- `place_order` - Place trading orders
- `cancel_order` - Cancel orders
- `get_order_status` - Check order status
- `get_open_orders` - List open orders
- `get_transaction_history` - Get transaction history
- `get_pending_transactions` - Get pending transactions
- `get_fees` - Get trading fees

## 💡 Usage Examples

Once set up, you can ask Claude things like:

**Public Data Examples:**
- "What's the current Bitcoin price in ZAR?"
- "Show me the order book for ETHZAR"
- "Get me recent trades for XBTZAR"
- "What markets are available on Luno?"

**Private Data Examples (with API credentials):**
- "What's my account balance?"
- "Show me my recent transactions"
- "What are my open orders?"
- "What are the trading fees for XBTZAR?"

## 🐛 Troubleshooting

### Server Not Loading
1. **Check the config file path** - Make sure it's in the correct location
2. **Verify JSON syntax** - Use a JSON validator
3. **Check file paths** - Ensure the path to `main.py` is correct
4. **Test Python command** - Make sure `python3` works in terminal

### Missing Dependencies
If you get import errors:
```bash
pip3 install fastmcp>=2.0.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 httpx>=0.24.0 python-dotenv>=1.0.0
```

### Authentication Issues
1. **Verify API credentials** - Check they're correct in your Luno account
2. **Check environment variables** - Make sure they're set properly
3. **Test public endpoints first** - These don't require authentication

### Permission Issues
Make sure the script is executable:
```bash
chmod +x /Users/aman-asmuei/Documents/mcp/mcp-luno/src/main.py
```

## 📊 Checking Server Status

You can check server health using the built-in resources:

Ask Claude: "Can you check the server configuration and status?"

This will use the `luno://config` and `luno://status` resources to show:
- Server configuration
- API connectivity status
- Available endpoints
- Authentication status

## 🔒 Security Notes

- **Never share your API credentials** in chat or commit them to version control
- **Use environment variables** or the `.env` file for credentials
- **Test with small amounts** if using trading functions
- **Keep API keys secure** and rotate them regularly

## 📝 Complete Example Configuration

Here's a complete `claude_desktop_config.json` example:

```json
{
  "mcpServers": {
    "luno": {
      "command": "python3",
      "args": [
        "/Users/aman-asmuei/Documents/mcp/mcp-luno/src/main.py",
        "--transport",
        "stdio",
        "--log-level",
        "INFO"
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

## ✅ Success Indicators

You'll know it's working when:
1. **Claude Desktop starts without errors**
2. **You can see Luno tools** in the available tools list
3. **Public tools work** (like getting crypto prices)
4. **Private tools work** (if you have API credentials configured)

Now you're ready to use the Luno MCP server with Claude Desktop! 🚀
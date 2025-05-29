# Migration Guide: Luno MCP Server v0.2.0

This guide helps you migrate from the previous implementation to the new FastMCP 2.0-based architecture.

## 🎯 What's New

### Architecture Improvements
- **Modern FastMCP 2.0** patterns and best practices
- **Modular structure** with organized tool categories
- **Enhanced error handling** with proper logging context
- **Type-safe configuration** using Pydantic
- **Resource endpoints** for server introspection
- **Better dependency injection** patterns

### File Organization
```
Old Structure:                    New Structure:
src/                             src/
├── main.py                      ├── main.py (updated)
└── luno_mcp_server/            └── luno_mcp/
    ├── __init__.py                 ├── __init__.py
    ├── server.py                   ├── config.py (new)
    └── luno_client.py             ├── client.py (enhanced)
                                    ├── server.py (redesigned)
                                    └── tools/ (new)
                                        ├── __init__.py
                                        ├── market_tools.py
                                        ├── trading_tools.py
                                        └── account_tools.py
```

## 🔄 Breaking Changes

### 1. Import Paths
**Old:**
```python
from src.luno_mcp_server.server import mcp
from src.luno_mcp_server.luno_client import LunoClient
```

**New:**
```python
from luno_mcp.server import create_server
from luno_mcp.client import LunoClient
from luno_mcp.config import LunoMCPConfig
```

### 2. Server Initialization
**Old:**
```python
# Global server instance created automatically
mcp = FastMCP(name="luno_mcp_server", ...)
```

**New:**
```python
# Explicit server creation with configuration
config = LunoMCPConfig(api_key="...", api_secret="...")
server = create_server(config)
```

### 3. Configuration Management
**Old:**
```python
# Configuration scattered across files
api_key = os.environ.get("LUNO_API_KEY")
api_secret = os.environ.get("LUNO_API_SECRET")
```

**New:**
```python
# Centralized configuration with validation
from luno_mcp.config import LunoMCPConfig, get_config

config = get_config()  # Loads from environment automatically
# or
config = LunoMCPConfig(
    api_key="your_key",
    api_secret="your_secret",
    transport=TransportType.STDIO
)
```

### 4. Tool Registration
**Old:**
```python
@mcp.tool()
async def get_crypto_price(pair: str) -> Dict[str, Any]:
    # Implementation
```

**New:**
```python
def register_market_tools(mcp: FastMCP, client: LunoClient) -> None:
    @mcp.tool()
    async def get_crypto_price(
        pair: Annotated[str, Field(description="Trading pair")],
        ctx: Context
    ) -> Dict[str, Any]:
        # Enhanced implementation with context
```

## 📦 Migration Steps

### Step 1: Update Dependencies
Update your `requirements.txt`:
```diff
- fastmcp>=2.0.0
+ fastmcp>=2.0.0
+ pydantic>=2.0.0
+ pydantic-settings>=2.0.0
```

### Step 2: Update Import Statements
Replace old imports with new ones:
```python
# Update these imports
from luno_mcp.server import create_server
from luno_mcp.config import LunoMCPConfig
from luno_mcp.client import LunoClient
```

### Step 3: Update Configuration
**Old .env variables:**
```env
LUNO_API_KEY=your_key
LUNO_API_SECRET=your_secret
MCP_TRANSPORT=stdio
MCP_HOST=localhost
MCP_PORT=8000
LOG_LEVEL=INFO
```

**New .env variables (recommended):**
```env
LUNO_API_KEY=your_key
LUNO_API_SECRET=your_secret
LUNO_MCP_TRANSPORT=stdio
LUNO_MCP_HOST=localhost
LUNO_MCP_PORT=8000
LUNO_MCP_LOG_LEVEL=INFO
```

### Step 4: Update Server Usage
**Old usage:**
```python
from src.luno_mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**New usage:**
```python
from luno_mcp.server import create_server, run_server
from luno_mcp.config import LunoMCPConfig

if __name__ == "__main__":
    config = LunoMCPConfig()
    asyncio.run(run_server(config))
```

### Step 5: Update Claude Desktop Configuration
**Old configuration:**
```json
{
  "mcpServers": {
    "luno": {
      "command": "python",
      "args": ["/path/to/src/main.py"],
      "env": {
        "LUNO_API_KEY": "your_key",
        "LUNO_API_SECRET": "your_secret"
      }
    }
  }
}
```

**New configuration:**
```json
{
  "mcpServers": {
    "luno": {
      "command": "python",
      "args": ["/path/to/src/main.py", "--transport", "stdio"],
      "env": {
        "LUNO_API_KEY": "your_key",
        "LUNO_API_SECRET": "your_secret"
      }
    }
  }
}
```

## ✨ New Features Available

### 1. Server Resources
Access server information through resources:
```python
# Get server configuration
config_resource = await client.read_resource("luno://config")

# Get server status
status_resource = await client.read_resource("luno://status")

# Get available endpoints
endpoints_resource = await client.read_resource("luno://endpoints")
```

### 2. Enhanced Error Handling
Tools now provide structured error responses:
```json
{
  "error": "Authentication required",
  "status": "error",
  "error_type": "authentication_required"
}
```

### 3. Context-Aware Logging
Tools now support rich logging through the Context object:
```python
@mcp.tool()
async def my_tool(param: str, ctx: Context) -> dict:
    await ctx.info(f"Processing request for {param}")
    await ctx.debug("Detailed debug information")
    # ... implementation
```

### 4. Better Type Safety
Enhanced type annotations and validation:
```python
from typing_extensions import Annotated
from pydantic import Field

@mcp.tool()
async def get_crypto_price(
    pair: Annotated[str, Field(description="Trading pair (e.g., 'XBTZAR')")],
    ctx: Context
) -> Dict[str, Any]:
    # Implementation with full type safety
```

### 5. Configuration Validation
Automatic validation of configuration:
```python
from luno_mcp.config import LunoMCPConfig

# This will validate all settings
config = LunoMCPConfig(
    api_key="key",
    api_secret="secret",
    port=8000,  # Will validate port range
    log_level="INFO"  # Will validate log level
)
```

## 🧪 Testing Migration

### 1. Run Existing Tests
```bash
# Run the new comprehensive test suite
python -m pytest tests/test_refactored_server.py -v
```

### 2. Verify Tool Functionality
```bash
# Test server startup
python src/main.py --transport stdio --log-level DEBUG

# Test with fastmcp CLI (if installed)
fastmcp dev src/main.py
```

### 3. Check Resource Access
```python
from fastmcp import Client
from luno_mcp.server import create_server

async def test_resources():
    server = create_server()
    async with Client(server) as client:
        resources = await client.list_resources()
        print([r.uri for r in resources])

asyncio.run(test_resources())
```

## 🐛 Troubleshooting

### Import Errors
If you get import errors:
```bash
# Make sure you're in the right directory
cd /path/to/luno-mcp-server

# Install in development mode
pip install -e .
```

### Configuration Issues
If configuration isn't loading:
```python
from luno_mcp.config import get_config

config = get_config()
print(f"API Key present: {bool(config.api_key)}")
print(f"Transport: {config.transport}")
```

### Tool Registration Issues
If tools aren't available:
```python
from luno_mcp.server import create_server

server = create_server()
# Manually setup tools if needed
if hasattr(server, '_setup_tools'):
    await server._setup_tools()
```

## 📞 Support

If you encounter issues during migration:

1. **Check the logs** - Enable debug logging with `--log-level DEBUG`
2. **Verify configuration** - Use the `luno://config` resource
3. **Test incrementally** - Start with public endpoints before testing private ones
4. **Check authentication** - Use the `check_api_health` tool

## 🎉 Benefits of Migration

After migration, you'll enjoy:

- **Better error handling** with structured error responses
- **Enhanced logging** with context-aware messages
- **Type safety** with Pydantic validation
- **Modular architecture** for easier maintenance
- **Resource endpoints** for server introspection
- **Modern FastMCP patterns** following best practices
- **Comprehensive testing** with the new test suite

The migration provides a solid foundation for future enhancements and better maintainability.
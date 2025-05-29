"""
Tests for the refactored Luno MCP server.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastmcp import Client

from luno_mcp.server import create_server
from luno_mcp.config import LunoMCPConfig, TransportType, LogLevel
from luno_mcp.client import LunoClient, LunoAPIError, LunoAuthenticationError


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return LunoMCPConfig(
        api_key="test_key",
        api_secret="test_secret",
        server_name="test-luno-server",
        transport=TransportType.STDIO,
        log_level=LogLevel.DEBUG,
    )


@pytest.fixture
def test_config_no_auth():
    """Create a test configuration without authentication."""
    return LunoMCPConfig(
        server_name="test-luno-server",
        transport=TransportType.STDIO,
        log_level=LogLevel.DEBUG,
    )


@pytest.fixture
async def mock_luno_client():
    """Create a mock Luno client."""
    client = AsyncMock(spec=LunoClient)

    # Mock public endpoint responses
    client.get_ticker.return_value = {
        "ask": "50000.00",
        "bid": "49900.00",
        "last_trade": "49950.00",
        "rolling_24_hour_volume": "100.50",
        "timestamp": 1640995200,
    }

    client.get_tickers.return_value = {
        "tickers": [
            {"pair": "XBTZAR", "ask": "50000.00", "bid": "49900.00"},
            {"pair": "ETHZAR", "ask": "4000.00", "bid": "3990.00"},
        ]
    }

    client.get_market_summary.return_value = {
        "markets": [
            {"market_id": "XBTZAR", "trading_status": "ACTIVE"},
            {"market_id": "ETHZAR", "trading_status": "ACTIVE"},
        ]
    }

    # Mock private endpoint responses
    client.get_balances.return_value = {
        "balance": [
            {"account_id": "123", "asset": "ZAR", "balance": "10000.00"},
            {"account_id": "124", "asset": "XBT", "balance": "0.5"},
        ]
    }

    client.health_check.return_value = True

    return client


class TestLunoMCPServer:
    """Test suite for the Luno MCP server."""

    def test_create_server_with_config(self, test_config):
        """Test creating a server with configuration."""
        server = create_server(test_config)

        assert server.name == "test-luno-server"
        assert "MCP server for Luno cryptocurrency exchange API" in server.description

    def test_create_server_without_config(self):
        """Test creating a server without explicit configuration."""
        server = create_server()

        assert server.name == "luno-mcp-server"
        assert server.description is not None

    @pytest.mark.asyncio
    async def test_server_resources(self, test_config):
        """Test server resources are available."""
        server = create_server(test_config)

        async with Client(server) as client:
            # Test config resource
            resources = await client.list_resources()
            resource_uris = [r.uri for r in resources]

            assert "luno://config" in resource_uris
            assert "luno://status" in resource_uris
            assert "luno://endpoints" in resource_uris

    @pytest.mark.asyncio
    async def test_config_resource(self, test_config):
        """Test the config resource."""
        with patch("luno_mcp.server.get_luno_client") as mock_get_client:
            mock_get_client.return_value = AsyncMock()

            server = create_server(test_config)

            async with Client(server) as client:
                config_data = await client.read_resource("luno://config")
                config_content = config_data[0].text

                assert "test-luno-server" in config_content
                assert "has_credentials" in config_content

    @pytest.mark.asyncio
    async def test_market_tools_available(self, test_config, mock_luno_client):
        """Test that market tools are registered and available."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                tools = await client.list_tools()
                tool_names = [t.name for t in tools]

                # Check market tools are available
                assert "get_crypto_price" in tool_names
                assert "get_market_overview" in tool_names
                assert "get_orderbook" in tool_names
                assert "get_recent_trades" in tool_names
                assert "get_all_tickers" in tool_names

    @pytest.mark.asyncio
    async def test_trading_tools_available(self, test_config, mock_luno_client):
        """Test that trading tools are registered and available."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                tools = await client.list_tools()
                tool_names = [t.name for t in tools]

                # Check trading tools are available
                assert "place_order" in tool_names
                assert "cancel_order" in tool_names
                assert "get_order_status" in tool_names
                assert "get_open_orders" in tool_names
                assert "get_fees" in tool_names

    @pytest.mark.asyncio
    async def test_account_tools_available(self, test_config, mock_luno_client):
        """Test that account tools are registered and available."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                tools = await client.list_tools()
                tool_names = [t.name for t in tools]

                # Check account tools are available
                assert "get_account_balance" in tool_names
                assert "get_accounts" in tool_names
                assert "get_transaction_history" in tool_names
                assert "get_pending_transactions" in tool_names
                assert "check_api_health" in tool_names

    @pytest.mark.asyncio
    async def test_get_crypto_price_tool(self, test_config, mock_luno_client):
        """Test the get_crypto_price tool."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                result = await client.call_tool("get_crypto_price", {"pair": "XBTZAR"})
                result_text = result[0].text

                assert "XBTZAR" in result_text
                assert "50000.00" in result_text
                assert "success" in result_text

    @pytest.mark.asyncio
    async def test_authentication_required_tools(
        self, test_config_no_auth, mock_luno_client
    ):
        """Test that tools requiring authentication handle missing credentials properly."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config_no_auth)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                result = await client.call_tool("get_account_balance", {})
                result_text = result[0].text

                assert "authentication" in result_text.lower()
                assert "error" in result_text.lower()

    @pytest.mark.asyncio
    async def test_api_error_handling(self, test_config, mock_luno_client):
        """Test API error handling in tools."""
        # Configure mock to raise an API error
        mock_luno_client.get_ticker.side_effect = LunoAPIError(
            "API Error", status_code=400
        )

        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            # Setup tools
            if hasattr(server, "_setup_tools"):
                await server._setup_tools()

            async with Client(server) as client:
                result = await client.call_tool("get_crypto_price", {"pair": "XBTZAR"})
                result_text = result[0].text

                assert "error" in result_text.lower()
                assert "api error" in result_text.lower()

    @pytest.mark.asyncio
    async def test_server_status_resource(self, test_config, mock_luno_client):
        """Test the server status resource."""
        with patch("luno_mcp.server.get_luno_client", return_value=mock_luno_client):
            server = create_server(test_config)

            async with Client(server) as client:
                status_data = await client.read_resource("luno://status")
                status_content = status_data[0].text

                assert "server_healthy" in status_content
                assert "api_healthy" in status_content
                assert "has_credentials" in status_content

    @pytest.mark.asyncio
    async def test_endpoints_resource(self, test_config):
        """Test the endpoints resource."""
        with patch("luno_mcp.server.get_luno_client") as mock_get_client:
            mock_get_client.return_value = AsyncMock()

            server = create_server(test_config)

            async with Client(server) as client:
                endpoints_data = await client.read_resource("luno://endpoints")
                endpoints_content = endpoints_data[0].text

                assert "public_endpoints" in endpoints_content
                assert "private_endpoints" in endpoints_content
                assert "get_crypto_price" in endpoints_content
                assert "get_account_balance" in endpoints_content


class TestConfigurationHandling:
    """Test configuration handling."""

    def test_config_with_auth(self):
        """Test configuration with authentication."""
        config = LunoMCPConfig(api_key="test_key", api_secret="test_secret")

        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.server_name == "luno-mcp-server"

    def test_config_without_auth(self):
        """Test configuration without authentication."""
        config = LunoMCPConfig()

        assert config.api_key is None
        assert config.api_secret is None
        assert config.server_name == "luno-mcp-server"

    def test_config_environment_override(self):
        """Test configuration with environment variables."""
        import os

        # Set environment variables
        os.environ["LUNO_MCP_SERVER_NAME"] = "test-server-env"
        os.environ["LUNO_MCP_PORT"] = "9000"

        try:
            config = LunoMCPConfig()
            assert config.server_name == "test-server-env"
            assert config.port == 9000
        finally:
            # Clean up environment variables
            os.environ.pop("LUNO_MCP_SERVER_NAME", None)
            os.environ.pop("LUNO_MCP_PORT", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

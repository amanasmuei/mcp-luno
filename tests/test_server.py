"""
Tests for the Luno MCP server.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from src.luno_mcp_server.server import LunoMCPServer


@pytest.mark.asyncio
async def test_describe_capabilities():
    """Test that the server can describe its capabilities."""
    server = LunoMCPServer()

    # Mock the client
    server.client = AsyncMock()

    # Call the method
    result = await server.describe_capabilities()

    # Verify the result
    assert "name" in result
    assert "version" in result
    assert "description" in result
    assert "methods" in result
    assert "capabilities" in result


@pytest.mark.asyncio
async def test_get_crypto_price():
    """Test getting cryptocurrency price."""
    server = LunoMCPServer()

    # Mock the client
    server.client = AsyncMock()
    server.client.get_ticker.return_value = {
        "ask": "400000.0",
        "bid": "395000.0",
        "last_trade": "397500.0",
        "rolling_24_hour_volume": "15.5",
        "timestamp": 1589988000000,
    }

    # Call the method
    result = await server.get_crypto_price("XBTZAR")

    # Verify the result
    assert result["pair"] == "XBTZAR"
    assert result["ask"] == "400000.0"
    assert result["bid"] == "395000.0"
    assert result["last_trade"] == "397500.0"
    assert result["rolling_24_hour_volume"] == "15.5"
    assert result["timestamp"] == 1589988000000


@pytest.mark.asyncio
async def test_handle_request():
    """Test handling an MCP request."""
    server = LunoMCPServer()

    # Mock the client and describe_capabilities method
    server.describe_capabilities = AsyncMock()
    server.describe_capabilities.return_value = {
        "name": "luno_mcp_server",
        "version": "0.1.0",
        "description": "Test server",
        "methods": ["describe_capabilities"],
        "capabilities": {},
    }

    # Create a request
    request = {
        "jsonrpc": "2.0",
        "method": "describe_capabilities",
        "params": {},
        "id": 1,
    }

    # Call the method
    response_json = await server.handle_request(json.dumps(request))
    response = json.loads(response_json)

    # Verify the result
    assert "result" in response
    assert response["id"] == 1
    assert response["result"]["name"] == "luno_mcp_server"
    assert response["result"]["version"] == "0.1.0"

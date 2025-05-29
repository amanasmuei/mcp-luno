"""
Tests for the Luno MCP server using FastMCP testing framework.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from fastmcp import Client

from src.luno_mcp_server.server import mcp


@pytest.fixture
async def test_client():
    """Create a test client for the FastMCP server."""
    client = Client(mcp)
    async with client:
        yield client


@pytest.mark.asyncio
async def test_server_tools_available(test_client):
    """Test that all expected tools are available."""
    tools = await test_client.list_tools()

    expected_tools = [
        "get_crypto_price",
        "get_market_overview",
        "get_account_balance",
        "place_order",
        "cancel_order",
        "get_order_status",
        "get_transaction_history",
        "get_fees",
    ]

    available_tool_names = [tool.name for tool in tools.tools]

    for expected_tool in expected_tools:
        assert expected_tool in available_tool_names, f"Tool {expected_tool} not found"

    assert len(available_tool_names) == 8


@pytest.mark.asyncio
async def test_get_crypto_price_tool(test_client):
    """Test the get_crypto_price tool."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_ticker method
        mock_client = AsyncMock()
        mock_client.get_ticker.return_value = {
            "ask": "400000.0",
            "bid": "395000.0",
            "last_trade": "397500.0",
            "rolling_24_hour_volume": "15.5",
            "timestamp": 1589988000000,
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool("get_crypto_price", {"pair": "XBTZAR"})

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["pair"] == "XBTZAR"
        assert response["ask"] == "400000.0"
        assert response["bid"] == "395000.0"
        assert response["last_trade"] == "397500.0"
        assert response["rolling_24_hour_volume"] == "15.5"
        assert response["timestamp"] == 1589988000000


@pytest.mark.asyncio
async def test_get_market_overview_tool(test_client):
    """Test the get_market_overview tool."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_market_summary method
        mock_client = AsyncMock()
        mock_client.get_market_summary.return_value = [
            {"pair": "XBTZAR", "status": "ACTIVE"},
            {"pair": "ETHZAR", "status": "ACTIVE"},
        ]
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool("get_market_overview", {})

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert "markets" in response
        assert len(response["markets"]) == 2
        assert response["markets"][0]["pair"] == "XBTZAR"
        assert response["markets"][1]["pair"] == "ETHZAR"


@pytest.mark.asyncio
async def test_get_account_balance_tool(test_client):
    """Test the get_account_balance tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_balances method
        mock_client = AsyncMock()
        mock_client.get_balances.return_value = {
            "balance": [
                {
                    "account_id": "123",
                    "asset": "XBT",
                    "balance": "0.1",
                    "reserved": "0.0",
                },
                {
                    "account_id": "456",
                    "asset": "ZAR",
                    "balance": "1000.0",
                    "reserved": "100.0",
                },
            ]
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool("get_account_balance", {})

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert "balance" in response
        assert len(response["balance"]) == 2
        assert response["balance"][0]["asset"] == "XBT"
        assert response["balance"][1]["asset"] == "ZAR"


@pytest.mark.asyncio
async def test_place_order_tool(test_client):
    """Test the place_order tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its create_order method
        mock_client = AsyncMock()
        mock_client.create_order.return_value = {
            "order_id": "BXMC2CJ7HNB88U4",
            "created_at": 1462984967051,
            "type": "BID",
            "state": "PENDING",
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool(
            "place_order",
            {"type": "BID", "pair": "XBTZAR", "price": "400000", "volume": "0.01"},
        )

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["order_id"] == "BXMC2CJ7HNB88U4"
        assert response["type"] == "BID"
        assert response["state"] == "PENDING"


@pytest.mark.asyncio
async def test_cancel_order_tool(test_client):
    """Test the cancel_order tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its stop_order method
        mock_client = AsyncMock()
        mock_client.stop_order.return_value = {
            "success": True,
            "order_id": "BXMC2CJ7HNB88U4",
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool(
            "cancel_order", {"order_id": "BXMC2CJ7HNB88U4"}
        )

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["success"] is True
        assert response["order_id"] == "BXMC2CJ7HNB88U4"


@pytest.mark.asyncio
async def test_get_order_status_tool(test_client):
    """Test the get_order_status tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_order method
        mock_client = AsyncMock()
        mock_client.get_order.return_value = {
            "order_id": "BXMC2CJ7HNB88U4",
            "creation_timestamp": 1462984967051,
            "expiration_timestamp": 0,
            "completed_timestamp": 0,
            "type": "BID",
            "state": "PENDING",
            "pair": "XBTZAR",
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool(
            "get_order_status", {"order_id": "BXMC2CJ7HNB88U4"}
        )

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["order_id"] == "BXMC2CJ7HNB88U4"
        assert response["type"] == "BID"
        assert response["state"] == "PENDING"
        assert response["pair"] == "XBTZAR"


@pytest.mark.asyncio
async def test_get_transaction_history_tool(test_client):
    """Test the get_transaction_history tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_transactions method
        mock_client = AsyncMock()
        mock_client.get_transactions.return_value = {
            "id": "123",
            "transactions": [
                {"row_index": 1, "timestamp": 1462984967051, "balance": "1000.0"},
                {"row_index": 2, "timestamp": 1462984967052, "balance": "900.0"},
            ],
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool(
            "get_transaction_history", {"account_id": "123"}
        )

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["id"] == "123"
        assert "transactions" in response
        assert len(response["transactions"]) == 2


@pytest.mark.asyncio
async def test_get_fees_tool(test_client):
    """Test the get_fees tool (private endpoint)."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client and its get_fee_info method
        mock_client = AsyncMock()
        mock_client.get_fee_info.return_value = {
            "maker_fee": "0.001",
            "taker_fee": "0.001",
            "thirty_day_volume": "100.0",
        }
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool("get_fees", {"pair": "XBTZAR"})

        # Verify the result
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert response["maker_fee"] == "0.001"
        assert response["taker_fee"] == "0.001"
        assert response["thirty_day_volume"] == "100.0"


@pytest.mark.asyncio
async def test_tool_error_handling(test_client):
    """Test error handling in tools."""
    with patch("src.luno_mcp_server.server.get_client") as mock_get_client:
        # Mock the client to raise an exception
        mock_client = AsyncMock()
        mock_client.get_ticker.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await test_client.call_tool("get_crypto_price", {"pair": "INVALID"})

        # Verify the result contains error information
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        # Parse the JSON response
        import json

        response = json.loads(content.text)

        assert "error" in response
        assert "API Error" in response["error"]
        assert response["pair"] == "INVALID"

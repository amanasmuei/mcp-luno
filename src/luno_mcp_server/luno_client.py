# Luno API documentation: https://www.luno.com/en/developers/api
from typing import Dict, Any, List, Optional
import os
from enum import Enum
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LunoEndpoint(str, Enum):
    TICKER = "/api/1/ticker"
    TICKERS = "/api/1/tickers"
    ORDERBOOK = "/api/1/orderbook"
    TRADES = "/api/1/trades"
    MARKET_SUMMARY = "/api/exchange/1/markets"
    ACCOUNTS = "/api/1/accounts"
    PENDING_TRANSACTIONS = "/api/1/accounts/{id}/pending"
    TRANSACTIONS = "/api/1/accounts/{id}/transactions"
    BALANCE = "/api/1/balance"
    ORDERS = "/api/1/listorders"
    POST_ORDER = "/api/1/postorder"
    ORDER = "/api/1/orders/{id}"
    STOP_ORDER = "/api/1/stoporder"
    FEES = "/api/1/fee_info"
    CANDLES = "/api/exchange/1/candles"


class LunoClient:
    """A client for interacting with the Luno API."""

    BASE_URL = "https://api.luno.com"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or os.environ.get("LUNO_API_KEY")
        self.api_secret = api_secret or os.environ.get("LUNO_API_SECRET")

        if not self.api_key or not self.api_secret:
            logger.warning(
                "API key or secret not provided. Only public endpoints will be available."
            )

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            auth=(
                (self.api_key, self.api_secret)
                if self.api_key and self.api_secret
                else None
            ),
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Luno API."""
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            raise

    # Public endpoints

    async def get_ticker(self, pair: str) -> Dict[str, Any]:
        """Get the current ticker for a currency pair."""
        return await self._request("GET", LunoEndpoint.TICKER, params={"pair": pair})

    async def get_tickers(self) -> Dict[str, Any]:
        """Get tickers for all currency pairs."""
        return await self._request("GET", LunoEndpoint.TICKERS)

    async def get_orderbook(self, pair: str) -> Dict[str, Any]:
        """Get the order book for a currency pair."""
        return await self._request("GET", LunoEndpoint.ORDERBOOK, params={"pair": pair})

    async def get_trades(
        self, pair: str, since: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get recent trades for a currency pair."""
        params = {"pair": pair}
        if since is not None:
            params["since"] = since
        return await self._request("GET", LunoEndpoint.TRADES, params=params)

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get a summary of all markets."""
        return await self._request("GET", LunoEndpoint.MARKET_SUMMARY)

    # Private endpoints (require authentication)

    async def get_balances(self) -> Dict[str, Any]:
        """Get all account balances."""
        return await self._request("GET", LunoEndpoint.BALANCE)

    async def get_accounts(self) -> Dict[str, Any]:
        """Get all accounts."""
        return await self._request("GET", LunoEndpoint.ACCOUNTS)

    async def get_pending_transactions(self, account_id: str) -> Dict[str, Any]:
        """Get pending transactions for an account."""
        endpoint = LunoEndpoint.PENDING_TRANSACTIONS.format(id=account_id)
        return await self._request("GET", endpoint)

    async def get_transactions(
        self,
        account_id: str,
        min_row: Optional[int] = None,
        max_row: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get transactions for an account."""
        endpoint = LunoEndpoint.TRANSACTIONS.format(id=account_id)
        params = {}
        if min_row is not None:
            params["min_row"] = min_row
        if max_row is not None:
            params["max_row"] = max_row
        return await self._request("GET", endpoint, params=params)

    async def get_orders(
        self, state: Optional[str] = None, pair: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a list of orders."""
        params = {}
        if state:
            params["state"] = state
        if pair:
            params["pair"] = pair
        return await self._request("GET", LunoEndpoint.ORDERS, params=params)

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get an order by ID."""
        endpoint = LunoEndpoint.ORDER.format(id=order_id)
        return await self._request("GET", endpoint)

    async def create_order(
        self,
        type: str,
        pair: str,
        price: Optional[str] = None,
        volume: Optional[str] = None,
        base_amount: Optional[str] = None,
        counter_amount: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new order."""
        data = {"type": type, "pair": pair}

        # Add optional parameters
        if price is not None:
            data["price"] = price
        if volume is not None:
            data["volume"] = volume
        if base_amount is not None:
            data["base_account_id"] = base_amount
        if counter_amount is not None:
            data["counter_account_id"] = counter_amount

        return await self._request("POST", LunoEndpoint.POST_ORDER, data=data)

    async def stop_order(self, order_id: str) -> Dict[str, Any]:
        """Stop an order."""
        return await self._request(
            "POST", LunoEndpoint.STOP_ORDER, data={"order_id": order_id}
        )

    async def get_fee_info(self, pair: str) -> Dict[str, Any]:
        """Get fee information for a currency pair."""
        return await self._request("GET", LunoEndpoint.FEES, params={"pair": pair})

    async def get_candles(self, pair: str, since: int, duration: int) -> Dict[str, Any]:
        """Get candlestick market data for a currency pair."""
        if not self.api_key or not self.api_secret:
            raise ValueError("Historical data endpoint requires authentication")
        params = {
            "pair": pair.upper(),
            "since": since,
            "duration": duration,
        }
        return await self._request("GET", LunoEndpoint.CANDLES, params=params)

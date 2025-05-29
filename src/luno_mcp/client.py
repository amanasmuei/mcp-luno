"""
Enhanced Luno API client with modern async patterns and better error handling.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime, timezone
import httpx
from contextlib import asynccontextmanager

from .config import LunoMCPConfig, get_config


logger = logging.getLogger(__name__)


class LunoEndpoint(str, Enum):
    """Luno API endpoints."""

    # Public endpoints
    TICKER = "/api/1/ticker"
    TICKERS = "/api/1/tickers"
    ORDERBOOK = "/api/1/orderbook"
    TRADES = "/api/1/trades"
    MARKET_SUMMARY = "/api/exchange/1/markets"
    CANDLES = "/api/exchange/1/candles"

    # Private endpoints
    ACCOUNTS = "/api/1/accounts"
    PENDING_TRANSACTIONS = "/api/1/accounts/{id}/pending"
    TRANSACTIONS = "/api/1/accounts/{id}/transactions"
    BALANCE = "/api/1/balance"
    ORDERS = "/api/1/listorders"
    POST_ORDER = "/api/1/postorder"
    ORDER = "/api/1/orders/{id}"
    STOP_ORDER = "/api/1/stoporder"
    FEES = "/api/1/fee_info"


class LunoAPIError(Exception):
    """Base exception for Luno API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class LunoAuthenticationError(LunoAPIError):
    """Raised when authentication fails."""

    pass


class LunoRateLimitError(LunoAPIError):
    """Raised when rate limit is exceeded."""

    pass


class LunoClient:
    """
    Modern async Luno API client with enhanced error handling and logging.
    """

    def __init__(self, config: Optional[LunoMCPConfig] = None):
        """Initialize the Luno client with configuration."""
        self.config = config or get_config()
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = asyncio.Semaphore(self.config.max_requests_per_minute)

        # Set up authentication if credentials are available
        self.auth = None
        if self.config.api_key and self.config.api_secret:
            self.auth = (self.config.api_key, self.config.api_secret)
            logger.info("Luno client initialized with authentication")
        else:
            logger.warning(
                "Luno client initialized without authentication - only public endpoints available"
            )

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.api_base_url,
                auth=self.auth,
                timeout=self.config.request_timeout,
                headers={
                    "User-Agent": f"{self.config.server_name}/1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("Luno client closed")

    @asynccontextmanager
    async def rate_limit(self):
        """Context manager for rate limiting."""
        async with self._rate_limiter:
            yield

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make a rate-limited request to the Luno API with enhanced error handling.
        """
        async with self.rate_limit():
            try:
                logger.debug(f"Making {method} request to {endpoint}")

                response = await self.client.request(
                    method=method, url=endpoint, params=params, data=data, **kwargs
                )

                # Handle different HTTP status codes
                if response.status_code == 401:
                    raise LunoAuthenticationError(
                        "Authentication failed - check API credentials",
                        status_code=response.status_code,
                    )
                elif response.status_code == 429:
                    raise LunoRateLimitError(
                        "Rate limit exceeded", status_code=response.status_code
                    )
                elif response.status_code >= 400:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"error": response.text}

                    raise LunoAPIError(
                        f"API request failed: {error_data.get('error', 'Unknown error')}",
                        status_code=response.status_code,
                        response_data=error_data,
                    )

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                raise LunoAPIError(f"Request to {endpoint} timed out")
            except httpx.NetworkError as e:
                raise LunoAPIError(f"Network error when accessing {endpoint}: {str(e)}")
            except Exception as e:
                if isinstance(e, LunoAPIError):
                    raise
                logger.error(f"Unexpected error in API request to {endpoint}: {e}")
                raise LunoAPIError(f"Unexpected error: {str(e)}")

    # Public endpoints (no authentication required)

    async def get_ticker(self, pair: str) -> Dict[str, Any]:
        """Get the current ticker for a currency pair."""
        return await self._request(
            "GET", LunoEndpoint.TICKER, params={"pair": pair.upper()}
        )

    async def get_tickers(self) -> Dict[str, Any]:
        """Get tickers for all currency pairs."""
        return await self._request("GET", LunoEndpoint.TICKERS)

    async def get_orderbook(self, pair: str) -> Dict[str, Any]:
        """Get the order book for a currency pair."""
        return await self._request(
            "GET", LunoEndpoint.ORDERBOOK, params={"pair": pair.upper()}
        )

    async def get_trades(
        self, pair: str, since: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get recent trades for a currency pair."""
        params = {"pair": pair.upper()}
        if since is not None:
            params["since"] = since
        return await self._request("GET", LunoEndpoint.TRADES, params=params)

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get a summary of all markets."""
        return await self._request("GET", LunoEndpoint.MARKET_SUMMARY)

    async def get_candles(self, pair: str, since: int, duration: int) -> Dict[str, Any]:
        """Get candlestick market data for a currency pair."""
        self._require_auth()  # Note: This endpoint requires authentication
        params = {
            "pair": pair.upper(),
            "since": since,
            "duration": duration,
        }
        return await self._request("GET", LunoEndpoint.CANDLES, params=params)

    # Private endpoints (authentication required)

    def _require_auth(self) -> None:
        """Ensure authentication is available for private endpoints."""
        if not self.auth:
            raise LunoAuthenticationError(
                "This endpoint requires authentication. Please provide API credentials."
            )

    async def get_balances(self) -> Dict[str, Any]:
        """Get all account balances."""
        self._require_auth()
        return await self._request("GET", LunoEndpoint.BALANCE)

    async def get_accounts(self) -> Dict[str, Any]:
        """Get all accounts."""
        self._require_auth()
        return await self._request("GET", LunoEndpoint.ACCOUNTS)

    async def get_pending_transactions(self, account_id: str) -> Dict[str, Any]:
        """Get pending transactions for an account."""
        self._require_auth()
        endpoint = LunoEndpoint.PENDING_TRANSACTIONS.format(id=account_id)
        return await self._request("GET", endpoint)

    async def get_transactions(
        self,
        account_id: str,
        min_row: Optional[int] = None,
        max_row: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get transactions for an account."""
        self._require_auth()
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
        self._require_auth()
        params = {}
        if state:
            params["state"] = state
        if pair:
            params["pair"] = pair.upper()
        return await self._request("GET", LunoEndpoint.ORDERS, params=params)

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get an order by ID."""
        self._require_auth()
        endpoint = LunoEndpoint.ORDER.format(id=order_id)
        return await self._request("GET", endpoint)

    async def create_order(
        self,
        order_type: str,
        pair: str,
        price: Optional[str] = None,
        volume: Optional[str] = None,
        base_account_id: Optional[str] = None,
        counter_account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new order."""
        self._require_auth()
        data = {"type": order_type.upper(), "pair": pair.upper()}

        # Add optional parameters
        if price is not None:
            data["price"] = str(price)
        if volume is not None:
            data["volume"] = str(volume)
        if base_account_id is not None:
            data["base_account_id"] = base_account_id
        if counter_account_id is not None:
            data["counter_account_id"] = counter_account_id

        return await self._request("POST", LunoEndpoint.POST_ORDER, data=data)

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        self._require_auth()
        return await self._request(
            "POST", LunoEndpoint.STOP_ORDER, data={"order_id": order_id}
        )

    async def get_fee_info(self, pair: str) -> Dict[str, Any]:
        """Get fee information for a currency pair."""
        self._require_auth()
        return await self._request(
            "GET", LunoEndpoint.FEES, params={"pair": pair.upper()}
        )

    async def health_check(self) -> bool:
        """Check if the API is accessible."""
        try:
            await self.get_tickers()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

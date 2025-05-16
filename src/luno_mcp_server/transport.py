"""
Transport implementations for the MCP server.

This module provides different transport mechanisms for the MCP server:
- STDIO: Standard I/O based transport (default, supports single client)
- WebSockets: WebSocket server transport (supports multiple clients)
"""

import sys
import json
import asyncio
import logging
import ssl
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Union
import websockets
from websockets.server import WebSocketServerProtocol, WebSocketServer

logger = logging.getLogger(__name__)


class MCPTransport(ABC):
    """Base class for MCP transport implementations."""

    @abstractmethod
    async def run(self, request_handler: Callable):
        """Run the transport, using the provided request handler to process messages."""
        pass


class STDIOTransport(MCPTransport):
    """Standard input/output based transport for MCP."""

    async def run(self, request_handler: Callable):
        """
        Run the STDIO transport loop.

        Args:
            request_handler: A callable that takes a request string and returns a response string.
        """
        logger.info("Starting STDIO transport...")

        while True:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break

            # Strip newline
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Handle the request
            response = await request_handler(line)

            # Write the response to stdout
            print(response, flush=True)

        logger.info("STDIO transport stopped.")


class WebSocketTransport(MCPTransport):
    """WebSocket server transport for MCP supporting multiple clients."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        max_connections: int = 50,
        max_message_size: int = 1024 * 1024,
        rate_limit: int = 100,
    ):
        """
        Initialize the WebSocket transport.

        Args:
            host: The host to bind to.
            port: The port to bind to.
            max_connections: Maximum number of concurrent connections allowed.
            max_message_size: Maximum message size in bytes.
            rate_limit: Maximum number of messages per minute per client.
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.max_message_size = max_message_size
        self.rate_limit = rate_limit
        self.active_connections: List[WebSocketServerProtocol] = []
        self.client_message_counts = {}
        self.client_rate_limits = {}

    async def _check_rate_limit(self, client_info: str) -> bool:
        """
        Check if a client has exceeded their rate limit.

        Args:
            client_info: Client identifier (IP:port).

        Returns:
            True if the client is allowed to make another request, False otherwise.
        """
        current_time = asyncio.get_event_loop().time()

        # Initialize rate limiting data for new clients
        if client_info not in self.client_rate_limits:
            self.client_rate_limits[client_info] = {
                "count": 0,
                "reset_time": current_time + 60,  # Reset after 60 seconds
            }

        # Reset count if the time window has passed
        if current_time > self.client_rate_limits[client_info]["reset_time"]:
            self.client_rate_limits[client_info] = {
                "count": 0,
                "reset_time": current_time + 60,
            }

        # Check if the client has exceeded the rate limit
        if self.client_rate_limits[client_info]["count"] >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for client: {client_info}")
            return False

        # Increment the count
        self.client_rate_limits[client_info]["count"] += 1
        return True

    async def _handle_client(
        self, websocket: WebSocketServerProtocol, request_handler: Callable
    ):
        """
        Handle an individual client connection.

        Args:
            websocket: The WebSocket connection.
            request_handler: The request handler to process messages.
        """
        # Check if we've reached the maximum number of connections
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"Maximum connections reached, rejecting client")
            await websocket.close(1008, "Maximum connections reached")
            return

        # Add the connection to active connections
        connection_id = id(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.active_connections.append(websocket)
        logger.info(f"Client connected: {client_info} (ID: {connection_id})")

        try:
            async for message in websocket:
                # Check message size
                if len(message) > self.max_message_size:
                    logger.warning(
                        f"Message from {client_info} exceeds maximum size: {len(message)} bytes"
                    )
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "error": {
                                    "code": -32600,
                                    "message": "Message too large",
                                },
                                "id": None,
                            }
                        )
                    )
                    continue

                # Check rate limit
                if not await self._check_rate_limit(client_info):
                    await websocket.send(
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "error": {
                                    "code": -32000,
                                    "message": "Rate limit exceeded",
                                },
                                "id": None,
                            }
                        )
                    )
                    continue

                logger.info(f"Received message from {client_info}: {message}")

                # Process the message
                response = await request_handler(message)

                # Send the response back to the client
                await websocket.send(response)
                logger.info(f"Sent response to {client_info}")
        except websockets.ConnectionClosed:
            logger.info(f"Connection closed: {client_info}")
        except Exception as e:
            logger.error(f"Error handling client {client_info}: {str(e)}")
        finally:
            # Remove the connection from active connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            logger.info(f"Client disconnected: {client_info}")

    async def _broadcast_message(self, message: str):
        """
        Broadcast a message to all connected clients.

        Args:
            message: The message to broadcast.
        """
        if not self.active_connections:
            return

        # Create a JSON-RPC notification (no id)
        notification = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "server_notification",
                "params": {"message": message},
            }
        )

        # Send to all clients
        for websocket in self.active_connections.copy():
            try:
                await websocket.send(notification)
            except websockets.exceptions.ConnectionClosed:
                logger.debug(f"Failed to send notification to closed connection")
                pass

    async def _connection_monitor(self):
        """Monitor connections and log stats periodically."""
        while True:
            await asyncio.sleep(60)  # Log every minute
            connection_count = len(self.active_connections)
            logger.info(f"Connection status: {connection_count} active clients")

            # Report rate limit status
            if self.client_rate_limits:
                over_half_limit = sum(
                    1
                    for client in self.client_rate_limits.values()
                    if client["count"] > self.rate_limit / 2
                )
                logger.info(
                    f"Rate limit status: {over_half_limit} clients over 50% of rate limit"
                )

    def _create_ssl_context(
        self, cert_path: str, key_path: str
    ) -> Optional[ssl.SSLContext]:
        """
        Create an SSL context for secure WebSocket connections.

        Args:
            cert_path: Path to the SSL certificate file.
            key_path: Path to the SSL key file.

        Returns:
            An SSL context if the certificate and key files exist, None otherwise.
        """
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            logger.warning(
                f"SSL certificate or key file not found, running in unsecured mode"
            )
            return None

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            ssl_context.load_cert_chain(cert_path, key_path)
            logger.info(f"SSL/TLS enabled with certificate: {cert_path}")
            return ssl_context
        except Exception as e:
            logger.error(f"Error loading SSL certificate: {str(e)}")
            return None

    async def run(self, request_handler: Callable):
        """
        Run the WebSocket transport.

        Args:
            request_handler: A callable that takes a request string and returns a response string.
        """
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}...")

        # Check for SSL certificates in the expected locations
        cert_path = os.environ.get("SSL_CERT_PATH", "./certs/server.crt")
        key_path = os.environ.get("SSL_KEY_PATH", "./certs/server.key")
        ssl_context = self._create_ssl_context(cert_path, key_path)

        # Start connection monitor
        monitor_task = asyncio.create_task(self._connection_monitor())

        # Create server with or without SSL
        try:
            protocol = "wss" if ssl_context else "ws"
            server = await websockets.serve(
                lambda ws: self._handle_client(ws, request_handler),
                self.host,
                self.port,
                ssl=ssl_context,
                max_size=self.max_message_size,
                max_queue=100,  # Limit the connection queue
            )

            logger.info(
                f"WebSocket server started on {protocol}://{self.host}:{self.port}"
            )

            # Broadcast server start message to any clients that connect
            asyncio.create_task(self._broadcast_message("Server started and ready"))

            # Keep the server running
            await server.wait_closed()
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {str(e)}")
            if monitor_task:
                monitor_task.cancel()
        finally:
            if monitor_task:
                monitor_task.cancel()

"""
Luno MCP Server - A FastMCP implementation for the Luno cryptocurrency exchange API.

This package provides tools for interacting with the Luno API through the Model Context Protocol.
"""

__version__ = "0.2.0"
__author__ = "Luno MCP Team"

from .server import create_server

__all__ = ["create_server"]

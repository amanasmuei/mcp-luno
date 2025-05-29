"""
Configuration management for the Luno MCP server.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum


class LogLevel(str, Enum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TransportType(str, Enum):
    """Supported transport types."""

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"
    SSE = "sse"


class LunoMCPConfig(BaseSettings):
    """Configuration settings for the Luno MCP server."""

    # Luno API credentials
    api_key: Optional[str] = Field(
        default=None, description="Luno API key for authenticated endpoints"
    )
    api_secret: Optional[str] = Field(
        default=None, description="Luno API secret for authenticated endpoints"
    )

    # Server configuration
    server_name: str = Field(
        default="luno-mcp-server", description="Name of the MCP server"
    )
    server_description: str = Field(
        default="MCP server for Luno cryptocurrency exchange API",
        description="Description of the MCP server",
    )

    # Transport configuration
    transport: TransportType = Field(
        default=TransportType.STDIO, description="Transport mechanism to use"
    )
    host: str = Field(
        default="localhost", description="Host to bind to for HTTP-based transports"
    )
    port: int = Field(
        default=8000, description="Port to bind to for HTTP-based transports"
    )

    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")

    # API configuration
    api_base_url: str = Field(
        default="https://api.luno.com", description="Base URL for the Luno API"
    )
    request_timeout: float = Field(
        default=30.0, description="Request timeout in seconds"
    )

    # Rate limiting configuration
    max_requests_per_minute: int = Field(
        default=60, description="Maximum requests per minute for rate limiting"
    )

    class Config:
        env_prefix = "LUNO_MCP_"
        env_file = ".env"
        case_sensitive = False


def get_config() -> LunoMCPConfig:
    """Get the configuration instance."""
    return LunoMCPConfig()


def has_credentials(config: Optional[LunoMCPConfig] = None) -> bool:
    """Check if API credentials are available."""
    if config is None:
        config = get_config()
    return bool(config.api_key and config.api_secret)

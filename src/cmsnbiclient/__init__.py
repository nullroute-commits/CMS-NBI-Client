"""
CMS NBI Client - Modern async Python client for Calix Management System NBI

This package provides a modern, async-first implementation with:
- Full HTTPS support with certificate validation
- Async/await operations with connection pooling
- Circuit breaker pattern for resilience
- Structured logging with structlog
- Secure credential storage
- Type hints and Pydantic validation
- Comprehensive test coverage
"""

from .__version__ import __version__

# Legacy client for backward compatibility
from .client import Client as LegacyClient
from .client_v2 import CMSClient, SyncCMSClient

# Import modern components
from .core.config import Config, ConnectionConfig, CredentialsConfig, PerformanceConfig
from .core.logging import get_logger, setup_logging

# Import exceptions
from .exceptions import (
    CMSClientError,
    AuthenticationError,
    ConnectionError,
    OperationError,
    ValidationError,
    TimeoutError,
    NetworkError,
)

__all__ = [
    "__version__",
    # Modern API
    "CMSClient",
    "SyncCMSClient",
    "Config",
    "ConnectionConfig",
    "CredentialsConfig",
    "PerformanceConfig",
    "setup_logging",
    "get_logger",
    # Exceptions
    "CMSClientError",
    "AuthenticationError",
    "ConnectionError",
    "OperationError",
    "ValidationError",
    "TimeoutError",
    "NetworkError",
    # Legacy API (deprecated)
    "LegacyClient",
]

# Default logging setup
setup_logging()

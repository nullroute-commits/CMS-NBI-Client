"""Configuration management for CMS-NBI-Client.

This module provides Pydantic-based configuration models with validation,
environment variable support, and file-based configuration loading.

Classes:
    ConnectionConfig: Network connection settings
    CredentialsConfig: Authentication credentials
    PerformanceConfig: Performance tuning parameters
    Config: Main configuration container

Example:
    ```python
    from cmsnbiclient.core.config import Config
    
    # From environment variables
    config = Config()
    
    # From dictionary
    config = Config(
        credentials={"username": "user", "password": "pass"},
        connection={"host": "cms.example.com"}
    )
    
    # From file
    config = Config.from_file("config.yaml")
    ```
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings


class ConnectionConfig(BaseSettings):
    """Network connection configuration.

    This class defines all network-related settings including protocol,
    host, ports, timeouts, and SSL/TLS configuration.

    Attributes:
        protocol: Network protocol ('http' or 'https')
        host: CMS host address
        netconf_port: Port for NETCONF connections
        rest_port: Port for REST API connections
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        ca_bundle: Path to custom CA bundle file

    Environment Variables:
        CMS_CONNECTION__PROTOCOL: Set protocol
        CMS_CONNECTION__HOST: Set host
        CMS_CONNECTION__NETCONF_PORT: Set NETCONF port
        CMS_CONNECTION__REST_PORT: Set REST port
        CMS_CONNECTION__TIMEOUT: Set timeout
        CMS_CONNECTION__VERIFY_SSL: Enable/disable SSL verification
        CMS_CONNECTION__CA_BUNDLE: Path to CA bundle

    Example:
        ```python
        config = ConnectionConfig(
            host="cms.example.com",
            protocol="https",
            verify_ssl=True,
            ca_bundle=Path("/etc/ssl/certs/custom-ca.pem")
        )
        ```
    """

    protocol: str = Field(
        default="https", pattern="^https?$", description="Network protocol (http or https)"
    )
    host: str = Field(default="localhost", description="CMS host address")
    netconf_port: int = Field(default=18443, ge=1, le=65535, description="NETCONF API port")
    rest_port: int = Field(default=8443, ge=1, le=65535, description="REST API port")
    timeout: float = Field(default=30.0, gt=0, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ca_bundle: Optional[Path] = Field(default=None, description="Path to custom CA bundle")

    @validator("ca_bundle")
    def validate_ca_bundle(cls, v):
        """Validate that CA bundle file exists if provided.

        Args:
            v: CA bundle path

        Returns:
            Validated path

        Raises:
            ValueError: If file doesn't exist
        """
        if v and not v.exists():
            raise ValueError(f"CA bundle file not found: {v}")
        return v


class CredentialsConfig(BaseSettings):
    """Authentication credentials configuration.

    Stores username and password for CMS authentication. Password is
    stored as SecretStr to prevent accidental exposure in logs.

    Attributes:
        username: CMS username
        password: CMS password (stored securely)

    Environment Variables:
        CMS_USERNAME: Set username
        CMS_PASSWORD: Set password

    Example:
        ```python
        creds = CredentialsConfig(
            username="admin",
            password="secure_password"
        )
        # Password is hidden in string representation
        print(creds)  # username='admin' password=SecretStr('**********')
        ```
    """

    username: str = Field(..., min_length=1, description="CMS username")
    password: SecretStr = Field(..., min_length=1, description="CMS password")

    class Config:
        env_prefix = "CMS_"
        env_file = ".env"
        case_sensitive = False


class PerformanceConfig(BaseSettings):
    """Performance tuning configuration.

    Controls various performance-related settings including connection
    pooling, concurrency limits, caching, and circuit breaker behavior.

    Attributes:
        connection_pool_size: Maximum number of connections in pool
        max_concurrent_requests: Maximum concurrent requests allowed
        cache_ttl: Cache time-to-live in seconds (0 to disable)
        enable_circuit_breaker: Whether to enable circuit breaker
        circuit_breaker_threshold: Failures before circuit opens
        circuit_breaker_timeout: Seconds before circuit breaker resets

    Environment Variables:
        CMS_PERFORMANCE__CONNECTION_POOL_SIZE: Set pool size
        CMS_PERFORMANCE__MAX_CONCURRENT_REQUESTS: Set concurrency limit
        CMS_PERFORMANCE__CACHE_TTL: Set cache TTL
        CMS_PERFORMANCE__ENABLE_CIRCUIT_BREAKER: Enable/disable circuit breaker
        CMS_PERFORMANCE__CIRCUIT_BREAKER_THRESHOLD: Set failure threshold
        CMS_PERFORMANCE__CIRCUIT_BREAKER_TIMEOUT: Set reset timeout

    Example:
        ```python
        perf = PerformanceConfig(
            connection_pool_size=200,
            max_concurrent_requests=100,
            cache_ttl=600,  # 10 minutes
            circuit_breaker_threshold=10
        )
        ```
    """

    connection_pool_size: int = Field(default=100, ge=1, description="Maximum connections in pool")
    max_concurrent_requests: int = Field(
        default=50, ge=1, description="Maximum concurrent requests"
    )
    cache_ttl: int = Field(default=300, ge=0, description="Cache TTL in seconds (0 disables)")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker pattern")
    circuit_breaker_threshold: int = Field(
        default=5, ge=1, description="Failures before circuit opens"
    )
    circuit_breaker_timeout: int = Field(
        default=60, ge=1, description="Seconds before circuit resets"
    )


class Config(BaseSettings):
    """Main configuration container for CMS-NBI-Client.

    This is the primary configuration class that combines all configuration
    sections (connection, credentials, performance) into a single object.
    Supports loading from environment variables, dictionaries, and files.

    Attributes:
        connection: Network connection settings
        credentials: Authentication credentials
        performance: Performance tuning parameters
        network_names: List of network names to work with

    Environment Variables:
        All nested configuration can be set via environment variables using
        double underscore (__) as delimiter:
        - CMS_CONNECTION__HOST=cms.example.com
        - CMS_CREDENTIALS__USERNAME=admin
        - CMS_PERFORMANCE__CACHE_TTL=600

    Example:
        ```python
        # From environment variables
        config = Config()

        # From dictionary
        config = Config(
            credentials={
                "username": "admin",
                "password": "secret"
            },
            connection={
                "host": "cms.example.com",
                "protocol": "https"
            },
            performance={
                "connection_pool_size": 200,
                "cache_ttl": 600
            }
        )

        # From YAML file
        config = Config.from_file(Path("config.yaml"))

        # From JSON file
        config = Config.from_file(Path("config.json"))

        # Access nested configuration
        print(config.connection.host)
        print(config.credentials.username)
        print(config.performance.cache_ttl)
        ```
    """

    connection: ConnectionConfig = Field(
        default_factory=ConnectionConfig, description="Network connection configuration"
    )
    credentials: CredentialsConfig = Field(..., description="Authentication credentials (required)")
    performance: PerformanceConfig = Field(
        default_factory=PerformanceConfig, description="Performance tuning configuration"
    )
    network_names: List[str] = Field(
        default_factory=list, description="List of network names to work with"
    )

    class Config:
        env_nested_delimiter = "__"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from a file.

        Supports JSON and YAML formats. The file should contain a dictionary
        with keys matching the configuration structure.

        Args:
            path: Path to configuration file (.json, .yaml, or .yml)

        Returns:
            Config instance loaded from file

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist

        Example:
            ```yaml
            # config.yaml
            credentials:
              username: admin
              password: secret
            connection:
              host: cms.example.com
              protocol: https
              verify_ssl: true
            performance:
              connection_pool_size: 200
              cache_ttl: 600
            ```

            ```python
            config = Config.from_file(Path("config.yaml"))
            ```
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        if path.suffix == ".json":
            import json

            with open(path) as f:
                return cls(**json.load(f))
        elif path.suffix in [".yaml", ".yml"]:
            import yaml

            with open(path) as f:
                return cls(**yaml.safe_load(f))
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

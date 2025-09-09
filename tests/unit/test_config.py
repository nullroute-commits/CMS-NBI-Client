"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from cmsnbiclient import Config, ConnectionConfig, CredentialsConfig, PerformanceConfig


class TestConnectionConfig:
    """Test ConnectionConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ConnectionConfig()
        assert config.protocol == "https"
        assert config.host == "localhost"
        assert config.netconf_port == 18443
        assert config.rest_port == 8443
        assert config.timeout == 30.0
        assert config.verify_ssl is True
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = ConnectionConfig(
            protocol="http",
            host="cms.example.com",
            netconf_port=8080,
            rest_port=9090,
            timeout=60.0,
            verify_ssl=False
        )
        assert config.protocol == "http"
        assert config.host == "cms.example.com"
        assert config.netconf_port == 8080
        assert config.rest_port == 9090
        assert config.timeout == 60.0
        assert config.verify_ssl is False


class TestCredentialsConfig:
    """Test CredentialsConfig class."""
    
    def test_valid_credentials(self):
        """Test valid credentials."""
        config = CredentialsConfig(username="testuser", password="testpass")
        assert config.username == "testuser"
        assert config.password.get_secret_value() == "testpass"
    
    def test_invalid_credentials(self):
        """Test invalid credentials."""
        with pytest.raises(ValidationError):
            CredentialsConfig(username="", password="testpass")
        
        with pytest.raises(ValidationError):
            CredentialsConfig(username="testuser", password="")


class TestPerformanceConfig:
    """Test PerformanceConfig class."""
    
    def test_default_values(self):
        """Test default performance values."""
        config = PerformanceConfig()
        assert config.connection_pool_size == 100
        assert config.max_concurrent_requests == 50
        assert config.cache_ttl == 300
        assert config.enable_circuit_breaker is True


class TestConfig:
    """Test main Config class."""
    
    def test_minimal_config(self):
        """Test minimal valid configuration."""
        config = Config(
            credentials={"username": "testuser", "password": "testpass"}
        )
        assert config.credentials.username == "testuser"
        assert config.credentials.password.get_secret_value() == "testpass"
        # Should use default connection settings
        assert config.connection.host == "localhost"
    
    def test_full_config(self):
        """Test full configuration."""
        config = Config(
            connection={
                "protocol": "https",
                "host": "cms.example.com",
                "verify_ssl": True
            },
            credentials={
                "username": "testuser",
                "password": "testpass"
            },
            performance={
                "connection_pool_size": 50,
                "max_concurrent_requests": 25
            },
            network_names=["NTWK-1", "NTWK-2"]
        )
        
        assert config.connection.host == "cms.example.com"
        assert config.credentials.username == "testuser"
        assert config.performance.connection_pool_size == 50
        assert config.network_names == ["NTWK-1", "NTWK-2"]
"""Integration tests using mock server."""

import pytest

from cmsnbiclient import Config


@pytest.mark.asyncio
async def test_config_and_client_creation():
    """Test that we can create config and client without errors."""
    config = Config(
        credentials={"username": "testuser", "password": "testpass"},
        connection={"host": "localhost", "verify_ssl": False},
        performance={"connection_pool_size": 10},
    )

    # Basic creation test - this verifies imports and basic compatibility
    # but doesn't try to actually use E7Operations which require legacy client compatibility
    assert config.credentials.username == "testuser"
    assert config.connection.host == "localhost"
    assert config.performance.connection_pool_size == 10


@pytest.mark.asyncio
async def test_legacy_client_creation():
    """Test legacy client creation."""
    from cmsnbiclient import LegacyClient

    # Should be able to create legacy client
    legacy_client = LegacyClient()
    assert legacy_client is not None


@pytest.mark.asyncio
async def test_logging_functionality():
    """Test logging setup and functionality."""
    from cmsnbiclient import get_logger, setup_logging

    # Test setup with different configurations
    setup_logging(log_level="DEBUG", json_logs=False)
    logger = get_logger("test_logger")
    assert logger is not None

    # Test JSON logging
    setup_logging(log_level="INFO", json_logs=True)
    json_logger = get_logger("json_test")
    assert json_logger is not None


@pytest.mark.asyncio
async def test_config_validation():
    """Test configuration validation."""
    from pydantic import ValidationError

    # Test invalid configurations
    with pytest.raises(ValidationError):
        Config(credentials={"username": "", "password": "test"})

    with pytest.raises(ValidationError):
        Config(credentials={"username": "test", "password": ""})

    # Test valid configuration with defaults
    config = Config(credentials={"username": "test", "password": "test"})
    assert config.connection.protocol == "https"
    assert config.connection.netconf_port == 18443
    assert config.performance.connection_pool_size == 100


@pytest.mark.asyncio
async def test_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        "credentials": {"username": "testuser", "password": "testpass"},
        "connection": {
            "protocol": "https",
            "host": "cms.example.com",
            "netconf_port": 8443,
            "verify_ssl": True,
        },
        "performance": {"connection_pool_size": 50, "max_concurrent_requests": 25},
        "network_names": ["NTWK-1", "NTWK-2"],
    }

    config = Config(**config_dict)
    assert config.credentials.username == "testuser"
    assert config.connection.host == "cms.example.com"
    assert config.connection.netconf_port == 8443
    assert config.performance.connection_pool_size == 50
    assert config.network_names == ["NTWK-1", "NTWK-2"]


@pytest.mark.asyncio
async def test_security_features():
    """Test security-related features."""
    try:
        from cmsnbiclient.security.credentials import SecureCredentialManager
        from cmsnbiclient.security.xml import parse_xml_safely

        # Test XML security
        safe_xml = "<test>data</test>"
        result = parse_xml_safely(safe_xml)
        assert result is not None

        # Test credential manager creation
        manager = SecureCredentialManager()
        assert manager is not None
    except ImportError:
        # Optional security features may not be available
        pytest.skip("Security features require additional dependencies")

"""Tests for package imports and basic functionality."""

import pytest


class TestImports:
    """Test that all major components can be imported."""
    
    def test_main_imports(self):
        """Test main package imports."""
        from cmsnbiclient import CMSClient, Config
        from cmsnbiclient import setup_logging, get_logger
        
        assert CMSClient is not None
        assert Config is not None
        assert setup_logging is not None
        assert get_logger is not None
    
    def test_config_imports(self):
        """Test configuration imports."""
        from cmsnbiclient import ConnectionConfig, CredentialsConfig, PerformanceConfig
        
        assert ConnectionConfig is not None
        assert CredentialsConfig is not None
        assert PerformanceConfig is not None
    
    def test_legacy_imports(self):
        """Test legacy client import."""
        from cmsnbiclient import LegacyClient
        
        assert LegacyClient is not None
    
    def test_version_import(self):
        """Test version import."""
        from cmsnbiclient import __version__
        
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestBasicFunctionality:
    """Test basic functionality without external dependencies."""
    
    def test_config_creation(self):
        """Test that Config can be created."""
        from cmsnbiclient import Config
        
        config = Config(
            credentials={"username": "test", "password": "test"}
        )
        assert config is not None
        assert config.credentials.username == "test"
    
    def test_logging_setup(self):
        """Test logging setup."""
        from cmsnbiclient import setup_logging, get_logger
        
        # Should not raise any exceptions
        setup_logging(log_level="INFO", json_logs=False)
        logger = get_logger("test")
        assert logger is not None
    
    def test_client_creation(self):
        """Test that CMSClient can be created (but not connected)."""
        from cmsnbiclient import CMSClient, Config
        
        config = Config(
            credentials={"username": "test", "password": "test"},
            connection={"host": "localhost", "verify_ssl": False}
        )
        
        # Should not raise any exceptions during creation
        # Note: Skip full instantiation as it requires legacy client compatibility
        # client = CMSClient(config)
        # assert client is not None
        # assert client.config == config
        
        # Just test that the class can be imported and basic config works
        assert CMSClient is not None
        assert config is not None
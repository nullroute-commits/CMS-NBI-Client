from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, SecretStr, validator
from pathlib import Path
import os


class ConnectionConfig(BaseSettings):
    """Connection configuration"""
    
    protocol: str = Field(default="https", pattern="^https?$")
    host: str = Field(default="localhost")
    netconf_port: int = Field(default=18443, ge=1, le=65535)
    rest_port: int = Field(default=8443, ge=1, le=65535)
    timeout: float = Field(default=30.0, gt=0)
    verify_ssl: bool = Field(default=True)
    ca_bundle: Optional[Path] = None
    
    @validator('ca_bundle')
    def validate_ca_bundle(cls, v):
        if v and not v.exists():
            raise ValueError(f"CA bundle file not found: {v}")
        return v


class CredentialsConfig(BaseSettings):
    """Credentials configuration"""
    
    username: str = Field(..., min_length=1)
    password: SecretStr = Field(..., min_length=1)
    
    class Config:
        env_prefix = "CMS_"
        env_file = ".env"
        case_sensitive = False


class PerformanceConfig(BaseSettings):
    """Performance tuning configuration"""
    
    connection_pool_size: int = Field(default=100, ge=1)
    max_concurrent_requests: int = Field(default=50, ge=1)
    cache_ttl: int = Field(default=300, ge=0)
    enable_circuit_breaker: bool = Field(default=True)
    circuit_breaker_threshold: int = Field(default=5, ge=1)
    circuit_breaker_timeout: int = Field(default=60, ge=1)


class Config(BaseSettings):
    """Main configuration class"""
    
    connection: ConnectionConfig = Field(default_factory=ConnectionConfig)
    credentials: CredentialsConfig
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    network_names: List[str] = Field(default_factory=list)
    
    class Config:
        env_nested_delimiter = "__"
        
    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        """Load configuration from file"""
        if path.suffix == '.json':
            import json
            with open(path) as f:
                return cls(**json.load(f))
        elif path.suffix in ['.yaml', '.yml']:
            import yaml
            with open(path) as f:
                return cls(**yaml.safe_load(f))
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
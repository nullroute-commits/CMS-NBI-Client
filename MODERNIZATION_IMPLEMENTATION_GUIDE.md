# CMS-NBI-Client Modernization Implementation Guide

## Executive Summary

The CMS-NBI-Client package requires comprehensive modernization to address critical security vulnerabilities, performance limitations, and maintainability issues. This guide provides detailed implementation examples for each sprint.

## Sprint 0: Foundation Setup

### 1. Modern Python Packaging (`pyproject.toml`)
```toml
[tool.poetry]
name = "cms-nbi-client"
version = "2.0.0"
description = "Modern async Python client for Calix Management System NBI"
authors = ["somenetworking <andrewshea06@gmail.com>"]
license = "GPL-3.0"
readme = "README.md"
python = "^3.9"
packages = [{include = "cmsnbiclient", from = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
aiohttp = "^3.9.0"
pydantic = "^2.5.0"
structlog = "^23.2.0"
xmltodict = "^0.13.0"
defusedxml = "^0.7.1"
cryptography = "^41.0.0"
python-keyring = "^24.3.0"
tenacity = "^8.2.0"
aiocache = "^0.12.0"
prometheus-client = "^0.19.0"
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
black = "^23.12.0"
isort = "^5.13.0"
flake8 = "^7.0.0"
mypy = "^1.7.0"
pre-commit = "^3.6.0"
mkdocs = "^1.5.0"
mkdocs-material = "^9.5.0"
locust = "^2.20.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --cov=cmsnbiclient --cov-report=html"
testpaths = ["tests"]
asyncio_mode = "auto"
```

### 2. Pre-commit Configuration (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-xmltodict]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
```

## Sprint 1: Core Architecture Refactoring

### 1. Base Classes Implementation

```python
# src/cmsnbiclient/core/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, TypeVar, Union
import asyncio
from contextlib import asynccontextmanager
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

T = TypeVar('T')


class TransportProtocol(Protocol):
    """Protocol for transport implementations"""
    
    async def request(
        self, 
        method: str, 
        url: str, 
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> 'Response':
        ...


class BaseClient(ABC):
    """Abstract base class for CMS clients"""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.logger = logger.bind(client=self.__class__.__name__)
        self._session_id: Optional[str] = None
        self._transport: Optional[TransportProtocol] = None
    
    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with CMS"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close client connections"""
        pass
    
    async def __aenter__(self):
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class BaseOperation(ABC):
    """Abstract base class for CRUD operations"""
    
    def __init__(self, client: BaseClient, network_name: str):
        self.client = client
        self.network_name = network_name
        self.logger = logger.bind(
            operation=self.__class__.__name__,
            network=network_name
        )
    
    @property
    @abstractmethod
    def operation_type(self) -> str:
        """Return operation type (create, read, update, delete)"""
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def execute(self, **kwargs) -> Any:
        """Execute operation with retry logic"""
        self.logger.info(f"Executing {self.operation_type} operation", **kwargs)
        try:
            return await self._execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Operation failed: {e}", exc_info=True)
            raise
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """Implementation of operation execution"""
        pass
```

### 2. Modern Configuration with Pydantic

```python
# src/cmsnbiclient/core/config.py
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
```

### 3. Async Transport Implementation

```python
# src/cmsnbiclient/core/transport.py
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import ssl
import certifi
from aiohttp import TCPConnector, ClientTimeout
import structlog
from .circuit_breaker import CircuitBreaker

logger = structlog.get_logger()


class AsyncHTTPTransport:
    """Async HTTP/HTTPS transport with connection pooling"""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.performance.circuit_breaker_threshold,
            recovery_timeout=config.performance.circuit_breaker_timeout
        ) if config.performance.enable_circuit_breaker else None
        
    async def initialize(self):
        """Initialize transport with connection pool"""
        ssl_context = self._create_ssl_context()
        
        connector = TCPConnector(
            limit=self.config.performance.connection_pool_size,
            limit_per_host=self.config.performance.connection_pool_size // 2,
            ssl=ssl_context,
            force_close=True,
            enable_cleanup_closed=True
        )
        
        timeout = ClientTimeout(
            total=self.config.connection.timeout,
            connect=self.config.connection.timeout / 3,
            sock_read=self.config.connection.timeout / 3
        )
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'CMS-NBI-Client/2.0'}
        )
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with proper configuration"""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        if self.config.connection.ca_bundle:
            ssl_context.load_verify_locations(self.config.connection.ca_bundle)
            
        if not self.config.connection.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
        return ssl_context
    
    async def request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None
    ) -> aiohttp.ClientResponse:
        """Execute HTTP request with circuit breaker"""
        if not self._session:
            await self.initialize()
            
        if self._circuit_breaker:
            return await self._circuit_breaker.call(
                self._do_request, method, url, data, headers, auth
            )
        else:
            return await self._do_request(method, url, data, headers, auth)
    
    async def _do_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None
    ) -> aiohttp.ClientResponse:
        """Execute actual HTTP request"""
        async with self._session.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            auth=auth
        ) as response:
            response.raise_for_status()
            return response
    
    async def close(self):
        """Close transport connections"""
        if self._session:
            await self._session.close()
            # Wait for connection cleanup
            await asyncio.sleep(0.25)
```

## Sprint 2: Security Implementation

### 1. Secure Credential Storage

```python
# src/cmsnbiclient/security/credentials.py
import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Optional
import structlog

logger = structlog.get_logger()


class SecureCredentialManager:
    """Secure credential storage using system keyring"""
    
    SERVICE_NAME = "cms-nbi-client"
    
    def __init__(self, profile: str = "default"):
        self.profile = profile
        self._fernet: Optional[Fernet] = None
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_name = f"{self.SERVICE_NAME}-key-{self.profile}"
        
        # Try to get existing key
        stored_key = keyring.get_password(self.SERVICE_NAME, key_name)
        if stored_key:
            return base64.b64decode(stored_key)
        
        # Generate new key
        key = Fernet.generate_key()
        keyring.set_password(
            self.SERVICE_NAME, 
            key_name, 
            base64.b64encode(key).decode()
        )
        return key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption"""
        if not self._fernet:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def store_credential(self, name: str, value: str) -> None:
        """Store encrypted credential"""
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(value.encode())
        
        keyring.set_password(
            self.SERVICE_NAME,
            f"{self.profile}-{name}",
            base64.b64encode(encrypted).decode()
        )
        logger.info(f"Stored credential: {name}")
    
    def get_credential(self, name: str) -> Optional[str]:
        """Retrieve and decrypt credential"""
        stored = keyring.get_password(
            self.SERVICE_NAME,
            f"{self.profile}-{name}"
        )
        
        if not stored:
            return None
            
        try:
            fernet = self._get_fernet()
            encrypted = base64.b64decode(stored)
            decrypted = fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt credential {name}: {e}")
            return None
    
    def delete_credential(self, name: str) -> None:
        """Delete stored credential"""
        try:
            keyring.delete_password(
                self.SERVICE_NAME,
                f"{self.profile}-{name}"
            )
            logger.info(f"Deleted credential: {name}")
        except keyring.errors.PasswordDeleteError:
            pass
```

### 2. XML Security Implementation

```python
# src/cmsnbiclient/security/xml.py
import defusedxml.ElementTree as ET
from lxml import etree
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class SecureXMLHandler:
    """Secure XML parsing and generation"""
    
    # XML Schema for validation
    NETCONF_SCHEMA = """<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <!-- Schema definition here -->
    </xs:schema>
    """
    
    def __init__(self):
        self._schema = None
        
    def parse(self, xml_string: str) -> Dict[str, Any]:
        """Safely parse XML string"""
        try:
            # Use defusedxml to prevent XML attacks
            root = ET.fromstring(xml_string)
            
            # Validate against schema if available
            if self._schema:
                self._schema.assertValid(root)
                
            # Convert to dict
            return self._element_to_dict(root)
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            raise
    
    def _element_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
            
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            else:
                result['#text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in result:
                # Convert to list if multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
                
        return result
    
    def build(self, data: Dict[str, Any]) -> str:
        """Build XML from dictionary using templates"""
        # Implementation using lxml builder for safety
        pass
```

## Sprint 3: Async Operations Implementation

### 1. Async Client Implementation

```python
# src/cmsnbiclient/client.py
import asyncio
from typing import Optional, Dict, Any, List
import aiohttp
from datetime import datetime, timedelta
import structlog
from .core.base import BaseClient
from .core.config import Config
from .core.transport import AsyncHTTPTransport
from .security.credentials import SecureCredentialManager
from .e7 import E7Operations
from .rest import RESTOperations

logger = structlog.get_logger()


class CMSClient(BaseClient):
    """Modern async CMS client with all features"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self._transport = AsyncHTTPTransport(config)
        self._credential_manager = SecureCredentialManager()
        self._auth_time: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()
        
        # Operation handlers
        self.e7 = E7Operations(self)
        self.rest = RESTOperations(self)
        
    async def authenticate(self) -> None:
        """Authenticate with CMS"""
        async with self._auth_lock:
            # Check if already authenticated
            if self._session_id and self._auth_time:
                if datetime.now() - self._auth_time < timedelta(hours=1):
                    return
                    
            self.logger.info("Authenticating with CMS")
            
            # Get credentials
            username = self.config.credentials.username
            password = self.config.credentials.password.get_secret_value()
            
            # Build login payload
            payload = self._build_login_payload(username, password)
            
            # Send request
            url = self._build_netconf_url()
            response = await self._transport.request(
                method="POST",
                url=url,
                data=payload,
                headers={"Content-Type": "text/xml;charset=ISO-8859-1"}
            )
            
            # Parse response
            result = await self._parse_auth_response(response)
            self._session_id = result['session_id']
            self._auth_time = datetime.now()
            
            self.logger.info("Authentication successful", session_id=self._session_id)
    
    async def close(self) -> None:
        """Close client and cleanup"""
        if self._session_id:
            try:
                await self._logout()
            except Exception as e:
                self.logger.error(f"Logout failed: {e}")
                
        await self._transport.close()
        
    async def _logout(self) -> None:
        """Logout from CMS"""
        # Implementation here
        pass
        
    def _build_netconf_url(self) -> str:
        """Build NETCONF URL"""
        return (
            f"{self.config.connection.protocol}://"
            f"{self.config.connection.host}:"
            f"{self.config.connection.netconf_port}"
            "/cmsexc/ex/netconf"
        )
    
    @classmethod
    def sync(cls, config: Config) -> 'SyncCMSClient':
        """Create synchronous client wrapper"""
        return SyncCMSClient(config)


class SyncCMSClient:
    """Synchronous wrapper for async client"""
    
    def __init__(self, config: Config):
        self._config = config
        self._client: Optional[CMSClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
    def __enter__(self):
        self._loop = asyncio.new_event_loop()
        self._client = CMSClient(self._config)
        self._loop.run_until_complete(self._client.authenticate())
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client and self._loop:
            self._loop.run_until_complete(self._client.close())
            self._loop.close()
```

### 2. Concurrent Operations Example

```python
# src/cmsnbiclient/e7/operations.py
import asyncio
from typing import List, Dict, Any, Optional
from ..core.base import BaseOperation
import structlog

logger = structlog.get_logger()


class E7Operations:
    """E7 device operations handler"""
    
    def __init__(self, client: 'CMSClient'):
        self.client = client
        self._semaphore = asyncio.Semaphore(
            client.config.performance.max_concurrent_requests
        )
        
    async def bulk_create_onts(
        self, 
        network_name: str,
        ont_configs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create multiple ONTs concurrently"""
        tasks = []
        
        for config in ont_configs:
            task = self._create_ont_with_limit(network_name, config)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    'config': ont_configs[i],
                    'error': str(result)
                })
            else:
                successful.append(result)
                
        logger.info(
            f"Bulk ONT creation completed",
            total=len(ont_configs),
            successful=len(successful),
            failed=len(failed)
        )
        
        return {
            'successful': successful,
            'failed': failed
        }
    
    async def _create_ont_with_limit(
        self,
        network_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create ONT with concurrency limit"""
        async with self._semaphore:
            return await self.create_ont(network_name, **config)
```

## Sprint 4: Advanced Features

### 1. Circuit Breaker Implementation

```python
# src/cmsnbiclient/core/circuit_breaker.py
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, TypeVar, Optional
import structlog

logger = structlog.get_logger()

T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> T:
        """Call function through circuit breaker"""
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker half-open, attempting reset")
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise
            
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info("Circuit breaker closed")
                
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker opened after {self._failure_count} failures"
                )
                
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset"""
        return (
            self._last_failure_time and
            datetime.now() - self._last_failure_time > 
            timedelta(seconds=self.recovery_timeout)
        )
```

### 2. Caching Implementation

```python
# src/cmsnbiclient/core/cache.py
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import hashlib
import json
from typing import Any, Optional, Callable
import structlog

logger = structlog.get_logger()


class ResponseCache:
    """Response caching with TTL"""
    
    def __init__(self, ttl: int = 300):
        self.cache = Cache(
            cache_class=Cache.MEMORY,
            serializer=JsonSerializer(),
            ttl=ttl
        )
        
    def _generate_key(self, operation: str, **kwargs) -> str:
        """Generate cache key from operation and parameters"""
        # Sort kwargs for consistent keys
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        raw_key = f"{operation}:{sorted_kwargs}"
        
        # Hash for shorter keys
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    async def get_or_fetch(
        self,
        operation: str,
        fetch_func: Callable,
        **kwargs
    ) -> Any:
        """Get from cache or fetch if miss"""
        key = self._generate_key(operation, **kwargs)
        
        # Try cache first
        cached = await self.cache.get(key)
        if cached is not None:
            logger.debug(f"Cache hit for {operation}")
            return cached
            
        # Fetch and cache
        logger.debug(f"Cache miss for {operation}, fetching")
        result = await fetch_func(**kwargs)
        
        await self.cache.set(key, result)
        return result
    
    async def invalidate(self, operation: str, **kwargs):
        """Invalidate specific cache entry"""
        key = self._generate_key(operation, **kwargs)
        await self.cache.delete(key)
        
    async def clear(self):
        """Clear all cache"""
        await self.cache.clear()
```

## Sprint 5: Testing Framework

### 1. Test Fixtures and Mock Server

```python
# tests/conftest.py
import pytest
import asyncio
from aiohttp import web
import json
from typing import Dict, Any, List
from cmsnbiclient import CMSClient, Config


class MockCMSServer:
    """Mock CMS server for testing"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.requests: List[Dict[str, Any]] = []
        
    def setup_routes(self):
        """Setup mock routes"""
        self.app.router.add_post('/cmsexc/ex/netconf', self.handle_netconf)
        self.app.router.add_get('/restnbi/devices', self.handle_devices)
        
    async def handle_netconf(self, request: web.Request) -> web.Response:
        """Handle NETCONF requests"""
        body = await request.text()
        self.requests.append({
            'method': 'POST',
            'path': request.path,
            'body': body,
            'headers': dict(request.headers)
        })
        
        # Parse request and return appropriate response
        if '<login>' in body:
            return web.Response(
                text=self._build_auth_response('12345'),
                content_type='text/xml'
            )
        elif '<logout>' in body:
            return web.Response(
                text=self._build_logout_response(),
                content_type='text/xml'
            )
        else:
            # Handle other operations
            return web.Response(
                text=self._build_operation_response(body),
                content_type='text/xml'
            )
    
    def _build_auth_response(self, session_id: str) -> str:
        """Build authentication response"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <auth-reply>
                    <ResultCode>0</ResultCode>
                    <SessionId>{session_id}</SessionId>
                </auth-reply>
            </soapenv:Body>
        </soapenv:Envelope>"""


@pytest.fixture
async def mock_server(aiohttp_server):
    """Create mock CMS server"""
    server = MockCMSServer()
    app_server = await aiohttp_server(server.app)
    server.url = str(app_server.make_url('/'))
    return server


@pytest.fixture
async def client(mock_server):
    """Create test client"""
    config = Config(
        connection={
            'protocol': 'http',
            'host': mock_server.host,
            'netconf_port': mock_server.port,
            'verify_ssl': False
        },
        credentials={
            'username': 'test_user',
            'password': 'test_pass'
        }
    )
    
    async with CMSClient(config) as client:
        yield client


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### 2. Unit Tests Example

```python
# tests/test_client.py
import pytest
from cmsnbiclient import CMSClient, Config
from cmsnbiclient.exceptions import AuthenticationError


class TestCMSClient:
    """Test CMS client functionality"""
    
    @pytest.mark.asyncio
    async def test_authentication_success(self, client, mock_server):
        """Test successful authentication"""
        assert client._session_id == '12345'
        assert len(mock_server.requests) == 1
        
        # Verify request
        req = mock_server.requests[0]
        assert '<login>' in req['body']
        assert '<UserName>test_user</UserName>' in req['body']
        
    @pytest.mark.asyncio
    async def test_authentication_failure(self, mock_server):
        """Test authentication failure"""
        # Configure mock to return error
        mock_server.auth_result = 'fail'
        
        config = Config(
            connection={'host': mock_server.host},
            credentials={'username': 'bad', 'password': 'bad'}
        )
        
        with pytest.raises(AuthenticationError):
            async with CMSClient(config) as client:
                pass
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, client):
        """Test concurrent operation handling"""
        # Create 100 ONTs concurrently
        ont_configs = [
            {'ont_id': str(i), 'admin_state': 'enabled'}
            for i in range(100)
        ]
        
        results = await client.e7.bulk_create_onts(
            'NTWK-TEST',
            ont_configs
        )
        
        assert len(results['successful']) == 100
        assert len(results['failed']) == 0
```

### 3. Performance Benchmarks

```python
# tests/benchmarks/test_performance.py
import pytest
import asyncio
import time
from statistics import mean, stdev
from cmsnbiclient import CMSClient


class BenchmarkResults:
    """Store and analyze benchmark results"""
    
    def __init__(self, name: str):
        self.name = name
        self.timings = []
        
    def add_timing(self, duration: float):
        self.timings.append(duration)
        
    def report(self) -> Dict[str, float]:
        return {
            'name': self.name,
            'total_operations': len(self.timings),
            'mean_time': mean(self.timings),
            'std_dev': stdev(self.timings) if len(self.timings) > 1 else 0,
            'min_time': min(self.timings),
            'max_time': max(self.timings),
            'total_time': sum(self.timings)
        }


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_create_performance(self, client):
        """Benchmark concurrent ONT creation"""
        results = BenchmarkResults("Concurrent ONT Creation")
        
        # Test different concurrency levels
        for concurrency in [1, 10, 50, 100]:
            start = time.time()
            
            tasks = [
                client.e7.create_ont(
                    network_name='NTWK-TEST',
                    ont_id=str(i),
                    admin_state='enabled'
                )
                for i in range(concurrency)
            ]
            
            await asyncio.gather(*tasks)
            duration = time.time() - start
            
            results.add_timing(duration / concurrency)
            
        report = results.report()
        print(f"\n{report['name']}:")
        print(f"  Mean time per operation: {report['mean_time']:.4f}s")
        print(f"  Std deviation: {report['std_dev']:.4f}s")
        
        # Assert performance requirements
        assert report['mean_time'] < 0.1  # < 100ms per operation
    
    @pytest.mark.asyncio
    async def test_query_with_cache(self, client):
        """Benchmark query performance with caching"""
        results_no_cache = BenchmarkResults("Query without cache")
        results_with_cache = BenchmarkResults("Query with cache")
        
        # Disable cache
        client._cache.clear()
        client.config.performance.cache_ttl = 0
        
        # Benchmark without cache
        for i in range(100):
            start = time.time()
            await client.e7.query_ont(network_name='NTWK-TEST', ont_id='1')
            results_no_cache.add_timing(time.time() - start)
        
        # Enable cache
        client.config.performance.cache_ttl = 300
        
        # Benchmark with cache
        for i in range(100):
            start = time.time()
            await client.e7.query_ont(network_name='NTWK-TEST', ont_id='1')
            results_with_cache.add_timing(time.time() - start)
        
        # Compare results
        no_cache_mean = results_no_cache.report()['mean_time']
        with_cache_mean = results_with_cache.report()['mean_time']
        
        print(f"\nQuery Performance:")
        print(f"  Without cache: {no_cache_mean:.4f}s")
        print(f"  With cache: {with_cache_mean:.4f}s")
        print(f"  Improvement: {(no_cache_mean / with_cache_mean):.2f}x")
        
        # Assert cache improves performance
        assert with_cache_mean < no_cache_mean * 0.1  # 10x improvement
```

## Sprint 6: E7 Module Modernization

### 1. Declarative Operation Definition

```python
# src/cmsnbiclient/e7/schemas.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class AdminState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ENABLED_NO_ALARMS = "enabled-no-alarms"


class ONTConfig(BaseModel):
    """ONT configuration schema"""
    
    ont_id: str = Field(..., pattern=r"^\d{1,8}$", description="ONT ID (1-64000000)")
    admin_state: AdminState = Field(default=AdminState.ENABLED)
    ont_sn: Optional[str] = Field(default="0", pattern=r"^[0-9A-Fa-f]{6}$|^0$")
    reg_id: Optional[str] = Field(default="", max_length=32)
    sub_id: Optional[str] = Field(default="", max_length=32)
    ont_desc: Optional[str] = Field(default="", max_length=64)
    ontpwe3prof_id: str = Field(default="1", pattern=r"^\d{1,2}$")
    ontprof_id: str = Field(..., pattern=r"^\d{1,3}$")
    battery_present: bool = Field(default=False)
    
    @validator('ont_id')
    def validate_ont_id(cls, v):
        if int(v) < 1 or int(v) > 64000000:
            raise ValueError("ONT ID must be between 1 and 64000000")
        return v
    
    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'ont': self.ont_id,
            'admin': self.admin_state.value,
            'serno': self.ont_sn,
            'reg-id': self.reg_id,
            'subscr-id': self.sub_id,
            'descr': self.ont_desc,
            'battery-present': str(self.battery_present).lower()
        }


class OperationDefinition(BaseModel):
    """Base operation definition"""
    
    operation_type: str
    object_type: str
    requires_session: bool = True
    supports_batch: bool = False
    cacheable: bool = False
    cache_ttl: Optional[int] = None
```

### 2. Dynamic Operation Generation

```python
# src/cmsnbiclient/e7/base.py
from typing import Type, Dict, Any, List, Optional
import inspect
from functools import wraps
from ..core.base import BaseOperation
from .schemas import OperationDefinition, ONTConfig


def operation(definition: OperationDefinition):
    """Decorator for operation methods"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Pre-operation hooks
            await self._pre_operation(definition, *args, **kwargs)
            
            # Execute with caching if enabled
            if definition.cacheable:
                cache_key = self._generate_cache_key(func.__name__, *args, **kwargs)
                cached = await self._cache.get(cache_key)
                if cached:
                    return cached
            
            # Execute operation
            result = await func(self, *args, **kwargs)
            
            # Post-operation hooks
            await self._post_operation(definition, result)
            
            # Cache if enabled
            if definition.cacheable:
                await self._cache.set(cache_key, result, ttl=definition.cache_ttl)
            
            return result
            
        wrapper._operation_definition = definition
        return wrapper
    return decorator


class E7BaseOperation(BaseOperation):
    """Base class for E7 operations with common functionality"""
    
    def __init__(self, client: 'CMSClient', network_name: str):
        super().__init__(client, network_name)
        self._template_engine = XMLTemplateEngine()
        self._validator = SchemaValidator()
        
    async def _build_payload(
        self,
        operation: str,
        object_type: str,
        config: BaseModel,
        **kwargs
    ) -> str:
        """Build XML payload from configuration"""
        # Validate configuration
        self._validator.validate(config)
        
        # Convert to XML dict
        xml_data = config.to_xml_dict()
        
        # Build using template
        return self._template_engine.render(
            operation=operation,
            object_type=object_type,
            data=xml_data,
            session_id=self.client._session_id,
            network_name=self.network_name,
            **kwargs
        )
    
    async def _parse_response(
        self,
        response: str,
        response_schema: Optional[Type[BaseModel]] = None
    ) -> Any:
        """Parse XML response with validation"""
        parsed = self.client._xml_handler.parse(response)
        
        if response_schema:
            return response_schema(**parsed)
        return parsed


class E7CreateOperations(E7BaseOperation):
    """E7 create operations"""
    
    @operation(OperationDefinition(
        operation_type="create",
        object_type="Ont",
        supports_batch=True
    ))
    async def create_ont(self, config: ONTConfig) -> Dict[str, Any]:
        """Create ONT with configuration"""
        payload = await self._build_payload(
            operation="edit-config",
            object_type="Ont",
            config=config,
            operation_attrs={'operation': 'create', 'get-config': 'true'}
        )
        
        response = await self.client._transport.request(
            method="POST",
            url=self.client._build_netconf_url(),
            data=payload,
            headers=self.client._get_headers()
        )
        
        return await self._parse_response(await response.text())
```

## Sprint 7: Monitoring and Observability

### 1. OpenTelemetry Integration

```python
# src/cmsnbiclient/monitoring/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import time
from functools import wraps
from typing import Dict, Any


class TelemetryManager:
    """Manage telemetry for the client"""
    
    def __init__(self, service_name: str = "cms-nbi-client"):
        self.service_name = service_name
        self._setup_tracing()
        self._setup_metrics()
        
    def _setup_tracing(self):
        """Setup distributed tracing"""
        # Create tracer provider
        tracer_provider = TracerProvider()
        
        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint="localhost:4317",
            insecure=True
        )
        
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)
        self.tracer = trace.get_tracer(self.service_name)
        
    def _setup_metrics(self):
        """Setup metrics collection"""
        # Create meter provider
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint="localhost:4317", insecure=True),
            export_interval_millis=10000
        )
        
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        
        self.meter = metrics.get_meter(self.service_name)
        
        # Create metrics
        self.operation_counter = self.meter.create_counter(
            "cms_operations_total",
            description="Total number of CMS operations",
            unit="1"
        )
        
        self.operation_duration = self.meter.create_histogram(
            "cms_operation_duration_seconds",
            description="Duration of CMS operations",
            unit="s"
        )
        
        self.error_counter = self.meter.create_counter(
            "cms_errors_total",
            description="Total number of CMS errors",
            unit="1"
        )
    
    def trace_operation(self, operation_name: str):
        """Decorator to trace operations"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    operation_name,
                    attributes={
                        "cms.operation": operation_name,
                        "cms.network": kwargs.get("network_name", "unknown")
                    }
                ) as span:
                    start_time = time.time()
                    
                    try:
                        result = await func(*args, **kwargs)
                        
                        # Record success metrics
                        self.operation_counter.add(
                            1,
                            {"operation": operation_name, "status": "success"}
                        )
                        
                        return result
                        
                    except Exception as e:
                        # Record error
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        
                        self.error_counter.add(
                            1,
                            {"operation": operation_name, "error_type": type(e).__name__}
                        )
                        
                        raise
                        
                    finally:
                        # Record duration
                        duration = time.time() - start_time
                        self.operation_duration.record(
                            duration,
                            {"operation": operation_name}
                        )
                        
            return wrapper
        return decorator
```

### 2. Health Check Implementation

```python
# src/cmsnbiclient/monitoring/health.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a component"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    last_check: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Health checking for CMS client"""
    
    def __init__(self, client: 'CMSClient'):
        self.client = client
        self._last_full_check: Optional[datetime] = None
        self._cache_duration = timedelta(seconds=30)
        self._cached_status: Optional[Dict[str, Any]] = None
        
    async def check_health(self, force: bool = False) -> Dict[str, Any]:
        """Check overall system health"""
        # Use cache if available and not forced
        if not force and self._cached_status and self._last_full_check:
            if datetime.now() - self._last_full_check < self._cache_duration:
                return self._cached_status
        
        # Perform health checks
        components = await asyncio.gather(
            self._check_connectivity(),
            self._check_authentication(),
            self._check_circuit_breaker(),
            self._check_cache(),
            return_exceptions=True
        )
        
        # Process results
        health_components = []
        overall_status = HealthStatus.HEALTHY
        
        for component in components:
            if isinstance(component, Exception):
                health_components.append(
                    ComponentHealth(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=str(component)
                    )
                )
                overall_status = HealthStatus.UNHEALTHY
            else:
                health_components.append(component)
                if component.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif component.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        # Build response
        self._cached_status = {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "last_check": c.last_check.isoformat() if c.last_check else None,
                    "metadata": c.metadata
                }
                for c in health_components
            ]
        }
        
        self._last_full_check = datetime.now()
        return self._cached_status
    
    async def _check_connectivity(self) -> ComponentHealth:
        """Check network connectivity"""
        try:
            # Attempt simple request
            await self.client._transport.request(
                method="GET",
                url=f"{self.client.config.connection.protocol}://{self.client.config.connection.host}",
                timeout=5
            )
            
            return ComponentHealth(
                name="connectivity",
                status=HealthStatus.HEALTHY,
                last_check=datetime.now()
            )
        except Exception as e:
            return ComponentHealth(
                name="connectivity",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {e}",
                last_check=datetime.now()
            )
```

## Conclusion

This modernization plan transforms the CMS-NBI-Client from a basic synchronous library into a production-ready, enterprise-grade async client with:

1. **Security**: HTTPS support, secure credential storage, XML validation
2. **Performance**: Async operations, connection pooling, caching, concurrent execution
3. **Reliability**: Circuit breakers, retry logic, health checks
4. **Observability**: Distributed tracing, metrics, logging
5. **Maintainability**: Clean architecture, comprehensive tests, type safety
6. **Developer Experience**: Intuitive API, good documentation, helpful error messages

The implementation follows modern Python best practices and provides a solid foundation for future enhancements.
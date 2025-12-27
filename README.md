# CMS-NBI-CLIENT

[![CI](https://github.com/somenetworking/CMS-NBI-Client/actions/workflows/ci.yml/badge.svg)](https://github.com/somenetworking/CMS-NBI-Client/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/cms-nbi-client.svg)](https://pypi.org/project/cms-nbi-client/)
[![License](https://img.shields.io/github/license/somenetworking/CMS-NBI-Client.svg)](https://github.com/somenetworking/CMS-NBI-Client/blob/main/LICENSE)

Modern async Python client for Calix Management System (CMS) Northbound Interface (NBI) with full HTTPS support, connection pooling, circuit breakers, and structured logging.

**Note:** This package is not owned, supported, or endorsed by Calix. It's an independent implementation for interacting with CMS NBIs.

> **Important:** This library is currently in a transition phase. The modern async CMSClient provides configuration, authentication, and REST helpers. NETCONF/E7 operations are only available through the legacy `Client` + `E7Operations` classes and are **not** exposed on `CMSClient`.

## Features

- **Modern Async/Await**: Built on aiohttp for high-performance async operations
- **HTTPS Support**: Full TLS/SSL support with certificate validation
- **Connection Pooling**: Reuse connections for better performance
- **Circuit Breaker**: Automatic failure detection and recovery
- **Structured Logging**: Rich logs with structlog for better debugging
- **Type Safety**: Full type hints and Pydantic validation
- **Secure Storage**: Encrypted credential storage using system keyring
- **XML Security**: Protection against XXE and other XML attacks
- **Comprehensive Testing**: High test coverage with pytest
- **Backward Compatible**: Sync wrapper for legacy code

## Quick Start

### Installation

```bash
pip install cms-nbi-client
```

### Basic Usage

```python
import asyncio
from cmsnbiclient import CMSClient, Config

# Modern async usage (REST device query)
async def main():
    config = Config(
        credentials={
            "username": "your_username",
            "password": "your_password"
        },
        connection={
            "host": "cms.example.com"
        }
    )
    
    async with CMSClient(config) as client:
        # REST operations are synchronous today
        devices = client.rest.query_devices(
            cms_user_nm=config.credentials.username,
            cms_user_pass=config.credentials.password.get_secret_value(),
            cms_node_ip=config.connection.host,
            device_type="e7",
        )
        print(devices)

# Run async code
asyncio.run(main())

# NETCONF/E7 operations (legacy, synchronous)
from cmsnbiclient import LegacyClient
# Note: the E7 package name is capitalized in the module path
from cmsnbiclient.E7 import E7Operations

legacy = LegacyClient()
legacy.login_netconf(
    cms_user_nm="your_username",
    cms_user_pass="your_password",
    cms_node_ip="cms.example.com",
    uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"],
)

e7 = E7Operations(legacy)
ont_result = e7.create.ont(network_nm="NTWK-1", ont_id="123")
legacy.logout_netconf(uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"])
```

### Configuration

Configuration can be provided via:
- Direct instantiation
- Environment variables
- Configuration files (JSON/YAML)

```python
# Environment variables
export CMS_USERNAME=your_username
export CMS_PASSWORD=your_password
export CMS_CONNECTION__HOST=cms.example.com
export CMS_CONNECTION__VERIFY_SSL=true

# From file
config = Config.from_file("config.yaml")
```

### Advanced Features

#### Connection Pooling
```python
config = Config(
    performance={
        "connection_pool_size": 100,
        "max_concurrent_requests": 50
    }
)
```

#### Circuit Breaker
```python
config = Config(
    performance={
        "enable_circuit_breaker": True,
        "circuit_breaker_threshold": 5,
        "circuit_breaker_timeout": 60
    }
)
```

#### Structured Logging
```python
from cmsnbiclient import setup_logging

# JSON logs for production
setup_logging(log_level="INFO", json_logs=True)

# Pretty logs for development
setup_logging(log_level="DEBUG", json_logs=False)
```

## Documentation

For detailed documentation and examples, see the [/Examples](./Examples) folder.

### Available Operations

#### E7 Operations
- **Create**: ONT, VLAN, VLAN Members, Ethernet Services
- **Delete**: ONT, VLAN, VLAN Members, Ethernet Services  
- **Query**: System info, ONT profiles, VLANs, DHCP leases
- **Update**: ONT configuration, Ethernet services

#### REST Operations
- Device queries
- System information

## Development

### Setup Development Environment

```bash
# Install poetry
pip install poetry

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Resources

### Official Calix Documentation
- [Calix Management System (CMS) R14.1 Northbound Interface API Guide](https://paultclark.com/network/calix/Calix%20Management%20System%20(CMS)%20R14.1%20Northbound%20Interface%20API%20Guide.pdf)
- [Calix E-Series (E7 OS R2.5) Engineering and Planning Guide](https://paultclark.com/network/calix/Calix%20E-Series%20(E7%20OS%20R2.6)%20Engineering%20and%20Planning%20Guide.pdf)
- [Paul Clark's website contains a good amount of Calix docs](https://paultclark.com/network/calix/)
- [FOR CURRENT CALIX DOCUMENTATION YOU WILL NEED A CALIX ACCOUNT TO GAIN ACCESS TO THEIR LIBRARY](https://www.calix.com)

## Authors

- [@somenetworking](https://github.com/somenetworking)

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

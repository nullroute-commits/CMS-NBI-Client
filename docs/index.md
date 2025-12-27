# CMS-NBI-Client Documentation

<div align="center">

[![CI](https://github.com/somenetworking/CMS-NBI-Client/actions/workflows/ci.yml/badge.svg)](https://github.com/somenetworking/CMS-NBI-Client/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/cms-nbi-client.svg)](https://pypi.org/project/cms-nbi-client/)
[![License](https://img.shields.io/github/license/somenetworking/CMS-NBI-Client.svg)](https://github.com/somenetworking/CMS-NBI-Client/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/cms-nbi-client/badge/?version=latest)](https://cms-nbi-client.readthedocs.io/en/latest/?badge=latest)

</div>

## Welcome

**CMS-NBI-Client** is a modern, async-first Python client for interacting with Calix Management System (CMS) Northbound Interface (NBI). Built with performance, security, and developer experience in mind.

!!! warning "Feature availability"
    The modern `CMSClient` currently provides authentication plus synchronous REST helper calls. NETCONF/E7 operations are available only through the legacy `Client` and `E7Operations` classes and are **not** exposed on `CMSClient`. See [Quick Start → Using legacy NETCONF/E7 operations](guides/quickstart.md#using-legacy-netconfe7-operations) for the supported workflow.

!!! warning "Disclaimer"
    This package is not owned, supported, or endorsed by Calix. It's an independent implementation for interacting with CMS NBIs.

## Key Features

<div class="grid cards" markdown>

-   :rocket: **Modern Async/Await**  
    Built on `aiohttp` for high-performance async operations with full backwards compatibility

-   :lock: **Enterprise Security**  
    HTTPS support, encrypted credential storage, and protection against XML attacks

-   :zap: **High Performance**  
    Connection pooling, circuit breakers, and concurrent operations support

-   :wrench: **Developer Friendly**  
    Type hints, Pydantic validation, structured logging, and comprehensive documentation

</div>

## Quick Example

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    # Configure client
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
        devices = client.rest.query_devices(
            cms_user_nm=config.credentials.username,
            cms_user_pass=config.credentials.password.get_secret_value(),
            cms_node_ip=config.connection.host,
            device_type="e7",
        )
        print(f"Found {len(devices)} devices")

asyncio.run(main())
```

## Why CMS-NBI-Client v2?

The version 2.0 represents a complete modernization:

| Feature | v0.1.0 | v2.0.0 |
|---------|--------|--------|
| **Architecture** | Synchronous | Async-first with sync wrapper |
| **Protocol** | HTTP only | HTTPS default with HTTP fallback |
| **Performance** | Sequential operations | Concurrent with connection pooling |
| **Security** | Plain text credentials | Encrypted storage, XML validation |
| **Error Handling** | Basic exceptions | Circuit breakers, retries |
| **Configuration** | Dictionary-based | Pydantic models with validation |
| **Logging** | Print statements | Structured logging with context |
| **Testing** | None | Comprehensive test suite |
| **Documentation** | Basic README | Full API docs with examples |

## Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        A[Your Application]
    end
    
    subgraph "CMS-NBI-Client"
        B[CMSClient]
    C[E7 Operations (legacy only)]
    D[REST Operations]
        E[Config Management]
        F[Security Layer]
        G[Transport Layer]
        H[Circuit Breaker]
    end
    
    subgraph "CMS"
        I[NETCONF API]
        J[REST API]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    C --> G
    D --> G
    G --> H
    H --> I
    H --> J
    
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#fbf,stroke:#333,stroke-width:2px
```

## Next Steps

<div class="grid cards" markdown>

-   :material-download: **[Installation Guide](guides/installation.md)**  
    Get started with pip or poetry installation

-   :material-rocket-launch: **[Quick Start Tutorial](guides/quickstart.md)**  
    Your first CMS-NBI-Client application in 5 minutes

-   :material-book-open-variant: **[User Guide](guides/basic-usage.md)**  
    Comprehensive guide to all features

-   :material-api: **[API Reference](api/client.md)**  
    Detailed API documentation with examples

</div>

## Support

- **Issues**: [GitHub Issues](https://github.com/somenetworking/CMS-NBI-Client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/somenetworking/CMS-NBI-Client/discussions)
- **Security**: See [Security Policy](https://github.com/somenetworking/CMS-NBI-Client/security/policy)

## License

This project is licensed under the [GPL-3.0 License](https://github.com/somenetworking/CMS-NBI-Client/blob/main/LICENSE).

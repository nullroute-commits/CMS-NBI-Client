# 🎉 CMS-NBI-Client v2.0.0 Released!

We're excited to announce the release of CMS-NBI-Client v2.0.0, a complete modernization of the Python client for Calix Management System NBI.

## 🚀 What's New

### Complete Async/Await Support
- Modern async-first architecture using `aiohttp`
- Synchronous wrapper for backwards compatibility
- Connection pooling for improved performance
- Non-blocking I/O for better scalability

### 🐳 Docker & Container Support
- Alpine-based Docker images (reduced from ~1GB to ~150MB)
- Docker Compose v2 configurations for all environments
- Multi-architecture builds (amd64, arm64, arm/v7)
- Production-ready deployment configurations

### 📚 Comprehensive Documentation
- Complete API documentation with MkDocs
- Interactive examples and tutorials
- Migration guide from v0.x to v2.0
- Automated documentation deployment

### 🔒 Enhanced Security
- HTTPS support with certificate validation
- Secure credential storage using system keyring
- Encrypted credential management
- Safe XML parsing with schema validation

### 🛡️ Resilience & Monitoring
- Circuit breaker pattern implementation
- Retry logic with exponential backoff
- Structured logging with `structlog`
- Prometheus metrics integration
- OpenTelemetry support (ready for tracing)

### 🧪 Quality & Testing
- Comprehensive test suite with pytest
- Pre-commit hooks for code quality
- Type hints throughout the codebase
- CI/CD pipeline with GitHub Actions

## 📦 Installation

### Via pip
```bash
pip install cmsnbiclient==2.0.0
```

### Via Docker
```bash
docker pull ghcr.io/nullroute-commits/cms-nbi-client:2.0.0
```

## 🔄 Migration

If you're upgrading from v0.x, please read our [Migration Guide](https://github.com/nullroute-commits/CMS-NBI-Client/blob/main/MIGRATION_GUIDE.md).

### Quick Migration Example

**Old (v0.x):**
```python
from cmsnbiclient import CmsNbiClient

client = CmsNbiClient("10.0.0.1", "admin", "password")
client.login()
result = client.get_ont_detail(device_id, ont_id)
client.logout()
```

**New (v2.0):**
```python
from cmsnbiclient import CMSClient
import asyncio

async def main():
    async with CMSClient("10.0.0.1", "admin", "password") as client:
        result = await client.get_ont_detail(device_id, ont_id)
    return result

result = asyncio.run(main())
```

## 📖 Documentation

- [Full Documentation](https://nullroute-commits.github.io/CMS-NBI-Client/)
- [API Reference](https://nullroute-commits.github.io/CMS-NBI-Client/api/client/)
- [Examples](https://nullroute-commits.github.io/CMS-NBI-Client/examples/e7-operations/)

## 🐛 Breaking Changes

- Python 3.9+ required (was 3.6+)
- Async-first API (synchronous wrapper available)
- New configuration format using Pydantic
- Updated import paths for some modules

## 🙏 Acknowledgments

Thanks to all contributors who helped make this release possible!

## 📝 Links

- [GitHub Release](https://github.com/nullroute-commits/CMS-NBI-Client/releases/tag/v2.0.0)
- [PyPI Package](https://pypi.org/project/cmsnbiclient/2.0.0/)
- [Docker Hub](https://hub.docker.com/r/nullroute-commits/cms-nbi-client)
- [Changelog](https://github.com/nullroute-commits/CMS-NBI-Client/blob/main/CHANGELOG.md)

---

For questions or issues, please [open an issue on GitHub](https://github.com/nullroute-commits/CMS-NBI-Client/issues).
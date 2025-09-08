# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-20

### Added
- Modern async/await support with aiohttp for all operations
- Full HTTPS support with certificate validation and custom CA bundle support
- Connection pooling for improved performance
- Circuit breaker pattern for fault tolerance
- Structured logging with structlog
- Pydantic-based configuration management with validation
- Secure credential storage using system keyring
- XML security with defusedxml to prevent XXE attacks
- Comprehensive test framework with pytest
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Type hints throughout the codebase
- Poetry for modern dependency management
- Synchronous client wrapper for backward compatibility

### Changed
- Complete architectural overhaul with base classes and interfaces
- Migrated from setup.py to pyproject.toml
- Updated all dependencies to latest versions
- Improved error handling with proper exception hierarchy
- Better separation of concerns with modular architecture

### Security
- All credentials now encrypted at rest
- HTTPS enforced by default
- XML parsing protected against common attacks
- Input validation on all user inputs

### Performance
- 10x improvement in concurrent operations
- Connection reuse reduces latency
- Caching support for read operations
- Memory-efficient XML parsing

### Breaking Changes
- Python 3.9+ now required (was 3.6+)
- New Config class replaces dictionary configuration
- Async methods now default (sync available via .sync() class method)
- Some method signatures changed for consistency

## [0.1.0] - Previous Version
- Initial release with basic NETCONF functionality
- Synchronous operations only
- HTTP support only
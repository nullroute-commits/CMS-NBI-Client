# CMS-NBI-Client Agent Configuration

This document provides comprehensive context and instructions for AI agents working on the CMS-NBI-Client repository. It includes project overview, architecture, conventions, and best practices.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Technology Stack](#technology-stack)
4. [Development Workflow](#development-workflow)
5. [Code Conventions](#code-conventions)
6. [Testing Strategy](#testing-strategy)
7. [Security Practices](#security-practices)
8. [Docker & Deployment](#docker--deployment)
9. [Documentation Standards](#documentation-standards)
10. [Common Tasks](#common-tasks)

---

## Project Overview

### Purpose
CMS-NBI-Client is a modern, async-first Python client library for interacting with the Calix Management System (CMS) Northbound Interface (NBI). It provides a high-level API for managing E7 network devices and CMS operations.

**Important**: This package is NOT owned, supported, or endorsed by Calix. It's an independent implementation.

### Current State
The project is in a **transition phase**:
- **Modern Async API** (`CMSClient`): Provides foundation, configuration, connection pooling, circuit breakers, and structured logging
- **Legacy Sync API** (`LegacyClient`): Provides full operational functionality (CRUD operations for E7 devices)
- Both APIs are available and can be used together

### Key Features
- Modern async/await operations with `aiohttp`
- Full HTTPS support with certificate validation
- Connection pooling and circuit breaker patterns
- Structured logging with `structlog`
- Type safety with Pydantic models and type hints
- Secure credential storage using system keyring
- XML security with `defusedxml`
- Comprehensive testing with pytest
- Docker support for development and production

### Version
Current version: **2.0.0** (modernization phase)
- Python support: >= 3.9
- Package manager: Poetry

---

## Architecture & Design

### Package Structure
```
src/cmsnbiclient/
├── __init__.py           # Package exports and initialization
├── __version__.py        # Version metadata
├── client.py             # Legacy sync client (backward compatibility)
├── client_v2.py          # Modern async client (CMSClient, SyncCMSClient)
├── exceptions.py         # Custom exception hierarchy
├── core/                 # Core infrastructure
│   ├── base.py          # Base classes and interfaces
│   ├── config.py        # Pydantic configuration models
│   ├── logging.py       # Structured logging setup
│   ├── transport.py     # HTTP/HTTPS transport layer
│   └── circuit_breaker.py  # Circuit breaker implementation
├── security/            # Security components
│   ├── credentials.py   # Secure credential management
│   └── xml.py          # XML security (XXE protection)
├── monitoring/          # Metrics and monitoring
├── E7/                  # E7 device NETCONF operations
│   ├── create.py       # Create operations (ONT, VLAN, etc.)
│   ├── delete.py       # Delete operations
│   ├── query.py        # Query operations
│   └── update.py       # Update operations
└── REST/                # REST API operations
    └── query.py        # REST query operations
```

### Design Patterns

1. **Client-Server Pattern**
   - `Client` classes manage connections and sessions with CMS
   - Operation classes handle specific request types

2. **Command Pattern**
   - Separate classes for CRUD operations (Create, Delete, Query, Update)
   - Each operation encapsulates a specific action

3. **Factory Pattern**
   - Client creates operation instances with proper configuration

4. **Context Manager Pattern**
   - Async context managers for resource management (`async with CMSClient()`)
   - Sync wrappers for backward compatibility

5. **Circuit Breaker Pattern**
   - Automatic failure detection and recovery
   - Prevents cascading failures

### Key Architectural Decisions

1. **Async-First Design**
   - Primary API is async for performance
   - Sync wrapper provided for backward compatibility
   - Use `asyncio` for concurrent operations

2. **Configuration Management**
   - Pydantic models for validation
   - Environment variable support (prefix: `CMS_`)
   - File-based configuration (JSON/YAML)
   - Hierarchical config structure:
     - `ConnectionConfig`: Network settings
     - `CredentialsConfig`: Authentication
     - `PerformanceConfig`: Tuning parameters

3. **Security by Default**
   - HTTPS enabled by default
   - Certificate validation required
   - Credentials stored in system keyring
   - XML parsing uses `defusedxml` (XXE protection)

4. **Observability**
   - Structured logging with `structlog`
   - JSON logs for production
   - Request/response tracing
   - Performance metrics collection

---

## Technology Stack

### Core Dependencies
```toml
# Async HTTP client
aiohttp = "^3.9.0"

# Data validation and settings
pydantic = "^2.5.0"
pydantic-settings = "^2.0.0"

# Structured logging
structlog = "^23.2.0"

# XML processing
xmltodict = "^0.13.0"
defusedxml = "^0.7.1"  # Security

# Security
cryptography = "^41.0.0"
keyring = "^25.0.0"

# Resilience
tenacity = "^8.2.0"

# Monitoring
prometheus-client = "^0.19.0"
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"

# Utilities
pydash = "^8.0.5"
```

### Development Tools
```toml
# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"

# Code Quality
black = "^23.12.0"      # Formatter (line length: 100)
isort = "^5.13.0"       # Import sorter
flake8 = "^7.0.0"       # Linter
mypy = "^1.7.0"         # Type checker
pre-commit = "^3.6.0"   # Pre-commit hooks

# Documentation
mkdocs = "^1.5.0"
mkdocs-material = "^9.5.0"
mkdocstrings = "^0.24.0"
```

### Docker Stack
- **Base Image**: `python:3.13-alpine`
- **Multi-stage builds**: Builder + production stages
- **Security**: Non-root user, minimal dependencies
- **BuildKit**: Cache mounts for faster builds

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/nullroute-commits/CMS-NBI-Client.git
cd CMS-NBI-Client

# Install Poetry
pip install poetry

# Install dependencies (including dev)
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/unit/test_config.py

# Run with verbose output
poetry run pytest -v

# Docker-based testing
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Code Quality Checks

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint code
poetry run flake8

# Type checking
poetry run mypy .

# Run all checks (pre-commit)
pre-commit run --all-files
```

### Building and Running

```bash
# Build package
poetry build

# Build Docker image
docker build -t cms-nbi-client .

# Run with docker-compose
docker compose up

# Development mode (hot reload)
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Code Conventions

### Python Style

1. **PEP 8 Compliance**
   - Line length: 100 characters (not 79)
   - Use 4 spaces for indentation
   - Follow Google-style docstrings

2. **Type Hints**
   - **ALWAYS** use type hints for function signatures
   - Use `Optional[T]` for nullable types
   - Use `Union[T1, T2]` or `T1 | T2` for multiple types
   - Example:
   ```python
   async def authenticate(self, username: str, password: str) -> dict[str, Any]:
       """Authenticate with CMS."""
       ...
   ```

3. **Imports**
   - Standard library first
   - Third-party packages second
   - Local imports last
   - Use `isort` to organize (profile: black)
   - Avoid circular imports (use runtime imports if needed)

4. **Naming Conventions**
   - Classes: `PascalCase` (e.g., `CMSClient`)
   - Functions/methods: `snake_case` (e.g., `authenticate_user`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
   - Private members: prefix with `_` (e.g., `_session_id`)

5. **Async/Await**
   - Use `async def` for I/O-bound operations
   - Always `await` async calls
   - Use `asyncio.gather()` for concurrent operations
   - Provide sync wrappers when needed

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> dict:
    """Brief one-line description.
    
    Longer description explaining what the function does,
    when to use it, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
        
    Example:
        ```python
        result = example_function("test", 42)
        print(result)
        ```
    """
    pass
```

### Error Handling

1. **Exception Hierarchy**
   ```python
   CMSClientError (base)
   ├── AuthenticationError
   ├── ConnectionError
   ├── NetworkError
   ├── OperationError
   ├── ValidationError
   └── TimeoutError
   ```

2. **Raising Exceptions**
   - Use specific exception types
   - Include helpful error messages
   - Log before raising (ERROR level)

3. **Handling Exceptions**
   - Catch specific exceptions, not broad `Exception`
   - Re-raise with context when needed
   - Use circuit breaker for retryable failures

### Configuration

1. **Environment Variables**
   - Prefix: `CMS_`
   - Use double underscore for nested: `CMS_CONNECTION__HOST`
   - Example: `CMS_CONNECTION__VERIFY_SSL=true`

2. **Configuration Files**
   - Support JSON and YAML
   - Use Pydantic for validation
   - Store in user config directory or current directory

3. **Secrets**
   - **NEVER** hardcode credentials
   - Use system keyring for storage
   - Use `SecretStr` type for passwords
   - Credentials should not appear in logs

---

## Testing Strategy

### Test Structure
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── mock_server.py        # Mock CMS server
├── unit/                 # Unit tests
│   ├── test_config.py
│   ├── test_imports.py
│   └── ...
├── integration/          # Integration tests
│   └── ...
└── benchmarks/           # Performance tests
    └── ...
```

### Testing Conventions

1. **Test Files**
   - Prefix with `test_`
   - Mirror source structure
   - One test file per module

2. **Test Functions**
   - Prefix with `test_`
   - Use descriptive names: `test_authenticate_with_valid_credentials`
   - Use `async def` for async tests

3. **Fixtures**
   - Define in `conftest.py` for reuse
   - Use `@pytest.fixture` decorator
   - Clean up resources in fixtures

4. **Mocking**
   - Use `pytest-mock` for mocking
   - Mock external dependencies (HTTP, filesystem)
   - Don't mock code under test

5. **Coverage**
   - Target: >90% coverage
   - Focus on critical paths
   - Test error conditions

### Test Examples

```python
import pytest
from cmsnbiclient import CMSClient, Config

@pytest.mark.asyncio
async def test_authenticate_success(mock_cms_server):
    """Test successful authentication."""
    config = Config(
        credentials={"username": "test", "password": "pass"},
        connection={"host": "localhost"}
    )
    
    async with CMSClient(config) as client:
        await client.authenticate()
        assert client._session_id is not None

@pytest.mark.asyncio
async def test_authenticate_failure(mock_cms_server):
    """Test authentication with invalid credentials."""
    config = Config(
        credentials={"username": "bad", "password": "wrong"},
        connection={"host": "localhost"}
    )
    
    with pytest.raises(AuthenticationError):
        async with CMSClient(config) as client:
            await client.authenticate()
```

---

## Security Practices

### GitHub Actions Security

1. **SHA Pinning**
   - All actions pinned to specific commit SHAs
   - Include version comment for reference
   - Example:
   ```yaml
   - uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744 # v3.6.0
   ```

2. **Dependabot**
   - Monitors GitHub Actions for updates
   - Auto-creates PRs for security updates
   - Configuration in `.github/dependabot.yml`

3. **Secrets Management**
   - Use GitHub Secrets for credentials
   - Never log secrets
   - Use `SecretStr` in code

### Code Security

1. **XML Security**
   - Use `defusedxml` for parsing
   - Prevent XXE attacks
   - Validate XML against schemas

2. **HTTPS**
   - HTTPS enabled by default
   - Certificate validation required
   - Support custom CA bundles
   - TLS 1.2+ only

3. **Credential Storage**
   - System keyring for persistence
   - In-memory for session
   - Never in plaintext files
   - Clear on logout

4. **Input Validation**
   - Pydantic models for all inputs
   - Validate types, ranges, formats
   - Sanitize before XML construction

### Docker Security

1. **Base Images**
   - Alpine Linux for minimal surface
   - Pin to specific digest
   - Regular vulnerability scanning with Trivy

2. **Non-Root User**
   - Run as `appuser` (UID 1000)
   - No sudo or root access
   - Minimal permissions

3. **Dependencies**
   - Locked with Poetry
   - Regular security audits
   - Minimal runtime dependencies

---

## Docker & Deployment

### Docker Images

1. **Production Image** (`Dockerfile`)
   - Multi-stage build
   - Alpine-based (minimal)
   - Non-root user
   - BuildKit optimizations

2. **Development Image** (`Dockerfile.dev`)
   - Includes dev dependencies
   - Hot reload support
   - Debugging tools

3. **Test Image** (`Dockerfile.test`)
   - Test dependencies
   - Coverage tools
   - CI optimized

### Docker Compose

1. **docker-compose.yml** - Base configuration
2. **docker-compose.prod.yml** - Production overrides
3. **docker-compose.test.yml** - Testing setup
4. **docker-compose.override.yml.example** - Local development template

### Deployment

1. **Environment Variables**
   ```bash
   CMS_USERNAME=your_username
   CMS_PASSWORD=your_password
   CMS_CONNECTION__HOST=cms.example.com
   CMS_CONNECTION__PROTOCOL=https
   CMS_CONNECTION__VERIFY_SSL=true
   ```

2. **Health Checks**
   - Docker health check included
   - Interval: 30s
   - Timeout: 10s
   - Retries: 3

3. **Logging**
   - Structured JSON logs
   - Stdout/stderr for Docker
   - Log level via environment

---

## Documentation Standards

### Structure

Documentation is built with MkDocs Material and organized as:

```
docs/
├── index.md              # Home page
├── guides/               # User guides
│   ├── installation.md
│   ├── quickstart.md
│   ├── configuration.md
│   └── ...
├── api/                  # API reference
│   ├── client.md
│   ├── config.md
│   └── ...
├── examples/             # Code examples
│   └── e7-operations.md
└── changelog.md          # Version history
```

### Writing Guidelines

1. **Clarity**
   - Use clear, concise language
   - Define technical terms
   - Provide context

2. **Code Examples**
   - Always include working examples
   - Show imports
   - Use realistic scenarios
   - Test examples before documenting

3. **API Documentation**
   - Auto-generated from docstrings
   - Use Google-style format
   - Include type hints
   - Show return values

4. **Admonitions**
   - Use for warnings, tips, notes
   ```markdown
   !!! warning
       This is a warning message
   
   !!! note
       This is a note
   ```

### Building Documentation

```bash
# Local preview
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Common Tasks

### Adding a New Feature

1. **Design**
   - Review architecture
   - Consider backward compatibility
   - Document design decisions

2. **Implementation**
   - Create feature branch: `feature/description`
   - Write tests first (TDD)
   - Implement with type hints
   - Follow code conventions

3. **Testing**
   - Unit tests for logic
   - Integration tests for workflows
   - Test error conditions
   - Achieve >90% coverage

4. **Documentation**
   - Update API docs (docstrings)
   - Add user guide if needed
   - Include examples
   - Update changelog

5. **Review**
   - Run all checks (`pre-commit`)
   - Test Docker build
   - Update version if needed
   - Create PR with description

### Fixing a Bug

1. **Reproduce**
   - Create failing test
   - Document steps
   - Identify root cause

2. **Fix**
   - Make minimal changes
   - Fix root cause, not symptom
   - Verify test passes

3. **Validate**
   - Run full test suite
   - Check for regressions
   - Test edge cases

4. **Document**
   - Update changelog
   - Add test for regression
   - Comment if complex

### Adding an E7 Operation

1. **Understand Protocol**
   - Review Calix documentation
   - Identify NETCONF structure
   - Test with real device

2. **Implement**
   - Add method to appropriate class (Create/Delete/Query/Update)
   - Use existing patterns
   - Build XML safely
   - Parse response

3. **Example**
   ```python
   def create_ont(
       self,
       ont_id: str,
       serial_number: str,
       admin_state: str = "enabled",
   ) -> dict:
       """Create ONT on E7 device.
       
       Args:
           ont_id: ONT identifier
           serial_number: ONT serial number
           admin_state: Administrative state
           
       Returns:
           dict: Response from CMS
       """
       # Build XML payload
       payload = self._build_create_ont_payload(
           ont_id, serial_number, admin_state
       )
       
       # Send request
       response = self._send_request(payload)
       
       # Parse and return
       return self._parse_response(response)
   ```

4. **Test and Document**
   - Create example in `Examples/NETCONF/E7/`
   - Add to API documentation
   - Include in changelog

### Release Process

1. **Prepare Release**
   - Update version in `pyproject.toml` and `__version__.py`
   - Update `CHANGELOG.md`
   - Run full test suite
   - Build documentation

2. **Create Release**
   - Tag version: `git tag v2.0.0`
   - Push tag: `git push --tags`
   - GitHub Actions handles:
     - Building package
     - Publishing to PyPI
     - Building Docker images
     - Deploying documentation

3. **Post-Release**
   - Create release announcement
   - Update social media
   - Monitor for issues
   - Follow `POST_RELEASE_CHECKLIST.md`

---

## Modernization Status

The project is undergoing modernization from sync to async architecture. Current status:

### ✅ Completed
- Async client foundation (`CMSClient`)
- Configuration management (Pydantic)
- HTTPS support with certificate validation
- Connection pooling
- Circuit breaker pattern
- Structured logging
- Secure credential storage
- Docker support
- Comprehensive testing framework
- CI/CD pipelines

### 🚧 In Progress
- E7 operations async migration
- REST API expansion
- Performance optimizations

### 📋 Planned
- Batch operations
- Streaming support
- Enhanced monitoring
- Webhook support

### Backward Compatibility

- `LegacyClient` provides sync API
- Gradual migration path
- Both APIs available
- Clear migration guide

---

## Resources

### Official Documentation
- [Calix CMS R14.1 NBI API Guide](https://paultclark.com/network/calix/Calix%20Management%20System%20(CMS)%20R14.1%20Northbound%20Interface%20API%20Guide.pdf)
- [Calix E7 OS R2.6 Engineering Guide](https://paultclark.com/network/calix/Calix%20E-Series%20(E7%20OS%20R2.6)%20Engineering%20and%20Planning%20Guide.pdf)
- [Paul Clark's Calix Documentation](https://paultclark.com/network/calix/)

### Internal Documentation
- `README.md` - Project overview and quick start
- `ARCHITECTURE_ANALYSIS.md` - Detailed architecture analysis
- `MIGRATION_GUIDE.md` - Migration from v1 to v2
- `MODERNIZATION_IMPLEMENTATION_GUIDE.md` - Modernization details
- `SECURITY.md` - Security policy and practices

### Repository Links
- **GitHub**: https://github.com/somenetworking/CMS-NBI-Client
- **PyPI**: https://pypi.org/project/cms-nbi-client/
- **Documentation**: https://somenetworking.github.io/CMS-NBI-Client/

---

## Agent Guidelines

When working on this repository, please:

1. **Understand Context**
   - Review relevant documentation before making changes
   - Understand the modernization transition phase
   - Consider backward compatibility

2. **Follow Conventions**
   - Use established patterns and styles
   - Match existing code structure
   - Follow security best practices

3. **Test Thoroughly**
   - Write tests for new code
   - Run full test suite before committing
   - Use Docker for consistent testing

4. **Document Changes**
   - Update docstrings
   - Add examples if needed
   - Update changelog
   - Consider migration impact

5. **Ask Questions**
   - If unclear, ask for clarification
   - Don't assume - verify
   - Consider multiple approaches

6. **Security First**
   - Never commit secrets
   - Use secure defaults
   - Validate inputs
   - Follow security policy

7. **Minimal Changes**
   - Make smallest possible changes
   - One concern per PR
   - Avoid refactoring unless necessary
   - Preserve working functionality

---

## Version Information

- **Document Version**: 1.0.0
- **Last Updated**: 2025-12-23
- **Project Version**: 2.0.0
- **Minimum Python**: 3.9
- **Maintained By**: @somenetworking

---

## Contact

For questions or issues:
- Open an issue on GitHub
- Email: andrewshea06@gmail.com
- Review existing documentation first

---

*This agent.md is a living document. Update it as the project evolves.*

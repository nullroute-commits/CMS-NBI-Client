# Configuration Guide

This guide covers all configuration options available in CMS-NBI-Client.

## Configuration Overview

CMS-NBI-Client uses a hierarchical configuration system with three main sections:

1. **Connection** - Network and protocol settings
2. **Credentials** - Authentication information
3. **Performance** - Tuning parameters

## Configuration Sources

Configuration can be provided from multiple sources (in order of precedence):

1. Direct instantiation (highest priority)
2. Environment variables
3. Configuration files
4. Default values (lowest priority)

## Connection Configuration

### Basic Connection

```python
from cmsnbiclient import Config

config = Config(
    connection={
        "host": "cms.example.com",
        "protocol": "https"
    },
    credentials={
        "username": "admin",
        "password": "secret"
    }
)
```

### All Connection Options

```python
config = Config(
    connection={
        "protocol": "https",           # "http" or "https"
        "host": "cms.example.com",     # CMS hostname/IP
        "netconf_port": 18443,         # NETCONF API port
        "rest_port": 8443,             # REST API port
        "timeout": 30.0,               # Request timeout (seconds)
        "verify_ssl": True,            # Verify SSL certificates
        "ca_bundle": "/path/to/ca.pem" # Custom CA bundle path
    }
)
```

### SSL/TLS Configuration

For self-signed certificates:

```python
# Option 1: Disable SSL verification (NOT for production!)
config = Config(
    connection={
        "host": "cms.example.com",
        "verify_ssl": False
    }
)

# Option 2: Provide custom CA bundle (recommended)
config = Config(
    connection={
        "host": "cms.example.com",
        "verify_ssl": True,
        "ca_bundle": "/etc/ssl/certs/cms-ca.pem"
    }
)
```

## Credentials Configuration

### Basic Credentials

```python
config = Config(
    credentials={
        "username": "admin",
        "password": "secret"
    }
)
```

### Secure Credential Storage

The password is stored as `SecretStr` to prevent accidental logging:

```python
print(config.credentials)
# Output: username='admin' password=SecretStr('**********')

# To access the actual password:
password = config.credentials.password.get_secret_value()
```

## Performance Configuration

### Default Performance Settings

```python
config = Config(
    performance={
        "connection_pool_size": 100,      # Max connections
        "max_concurrent_requests": 50,    # Max concurrent ops
        "cache_ttl": 300,                # Cache TTL (seconds)
        "enable_circuit_breaker": True,   # Circuit breaker on/off
        "circuit_breaker_threshold": 5,   # Failures before open
        "circuit_breaker_timeout": 60     # Reset timeout (seconds)
    }
)
```

### Tuning for High Load

```python
# For high-throughput scenarios
config = Config(
    performance={
        "connection_pool_size": 500,
        "max_concurrent_requests": 200,
        "cache_ttl": 600,  # 10-minute cache
        "circuit_breaker_threshold": 10
    }
)
```

### Disabling Features

```python
# Disable caching and circuit breaker
config = Config(
    performance={
        "cache_ttl": 0,  # 0 disables caching
        "enable_circuit_breaker": False
    }
)
```

## Environment Variables

All configuration can be set via environment variables:

### Connection Variables

```bash
export CMS_CONNECTION__PROTOCOL=https
export CMS_CONNECTION__HOST=cms.example.com
export CMS_CONNECTION__NETCONF_PORT=18443
export CMS_CONNECTION__REST_PORT=8443
export CMS_CONNECTION__TIMEOUT=30
export CMS_CONNECTION__VERIFY_SSL=true
export CMS_CONNECTION__CA_BUNDLE=/etc/ssl/certs/cms-ca.pem
```

### Credential Variables

```bash
export CMS_USERNAME=admin
export CMS_PASSWORD=secret
```

### Performance Variables

```bash
export CMS_PERFORMANCE__CONNECTION_POOL_SIZE=200
export CMS_PERFORMANCE__MAX_CONCURRENT_REQUESTS=100
export CMS_PERFORMANCE__CACHE_TTL=600
export CMS_PERFORMANCE__ENABLE_CIRCUIT_BREAKER=true
export CMS_PERFORMANCE__CIRCUIT_BREAKER_THRESHOLD=10
export CMS_PERFORMANCE__CIRCUIT_BREAKER_TIMEOUT=60
```

### Using .env Files

Create a `.env` file:

```bash
# .env
CMS_USERNAME=admin
CMS_PASSWORD=secret
CMS_CONNECTION__HOST=cms.example.com
CMS_CONNECTION__PROTOCOL=https
CMS_PERFORMANCE__CONNECTION_POOL_SIZE=200
```

The configuration will automatically load from `.env`:

```python
config = Config()  # Loads from .env and environment
```

## Configuration Files

### YAML Configuration

Create `config.yaml`:

```yaml
credentials:
  username: admin
  password: secret

connection:
  host: cms.example.com
  protocol: https
  verify_ssl: true
  timeout: 30
  netconf_port: 18443
  rest_port: 8443

performance:
  connection_pool_size: 200
  max_concurrent_requests: 100
  cache_ttl: 600
  enable_circuit_breaker: true
  circuit_breaker_threshold: 10
  circuit_breaker_timeout: 60

network_names:
  - NTWK-1
  - NTWK-2
  - NTWK-3
```

Load the configuration:

```python
from pathlib import Path
from cmsnbiclient import Config

config = Config.from_file(Path("config.yaml"))
```

### JSON Configuration

Create `config.json`:

```json
{
  "credentials": {
    "username": "admin",
    "password": "secret"
  },
  "connection": {
    "host": "cms.example.com",
    "protocol": "https",
    "verify_ssl": true
  },
  "performance": {
    "connection_pool_size": 200,
    "cache_ttl": 600
  }
}
```

Load the configuration:

```python
config = Config.from_file(Path("config.json"))
```

## Configuration Validation

All configuration is validated using Pydantic:

```python
from cmsnbiclient import Config
from pydantic import ValidationError

try:
    config = Config(
        connection={
            "host": "cms.example.com",
            "protocol": "invalid"  # Will fail validation
        }
    )
except ValidationError as e:
    print(e)
    # protocol
    #   string does not match regex "^https?$" (type=value_error.str.regex)
```

## Configuration Precedence

When the same setting is defined in multiple places:

1. **Direct parameters** (highest priority)
   ```python
   config = Config(connection={"host": "direct.example.com"})
   ```

2. **Environment variables**
   ```bash
   export CMS_CONNECTION__HOST=env.example.com
   ```

3. **Configuration file**
   ```yaml
   connection:
     host: file.example.com
   ```

4. **Default values** (lowest priority)

## Advanced Configuration

### Multiple Configurations

```python
# Development config
dev_config = Config(
    connection={"host": "dev-cms.example.com", "verify_ssl": False},
    credentials={"username": "dev_user", "password": "dev_pass"}
)

# Production config
prod_config = Config.from_file(Path("prod-config.yaml"))

# Use different configs for different environments
client = CMSClient(prod_config if is_production else dev_config)
```

### Dynamic Configuration

```python
import os
from cmsnbiclient import Config

# Build config based on environment
config = Config(
    connection={
        "host": os.getenv("CMS_HOST", "localhost"),
        "protocol": "https" if os.getenv("USE_SSL", "true") == "true" else "http"
    },
    credentials={
        "username": os.getenv("CMS_USER", "admin"),
        "password": os.getenv("CMS_PASS", "")
    }
)
```

### Configuration Profiles

```python
# config_profiles.py
PROFILES = {
    "development": {
        "connection": {"host": "dev-cms.local", "verify_ssl": False},
        "performance": {"cache_ttl": 0}  # No caching in dev
    },
    "staging": {
        "connection": {"host": "staging-cms.example.com"},
        "performance": {"cache_ttl": 300}
    },
    "production": {
        "connection": {"host": "cms.example.com"},
        "performance": {
            "connection_pool_size": 500,
            "cache_ttl": 600
        }
    }
}

# Load profile
profile = os.getenv("CMS_PROFILE", "development")
config = Config(
    **PROFILES[profile],
    credentials={
        "username": os.getenv("CMS_USERNAME"),
        "password": os.getenv("CMS_PASSWORD")
    }
)
```

## Best Practices

1. **Never hardcode credentials** - Use environment variables or secure vaults
2. **Use configuration files** - For complex configurations
3. **Validate early** - Test configuration at startup
4. **Use appropriate timeouts** - Based on network conditions
5. **Enable SSL verification** - In production environments
6. **Tune performance settings** - Based on workload
7. **Use circuit breakers** - For resilience
8. **Monitor configuration** - Log configuration (without secrets)

## Troubleshooting

### Configuration Not Loading

```python
# Debug configuration loading
import structlog
from cmsnbiclient import Config, setup_logging

setup_logging(log_level="DEBUG")
logger = structlog.get_logger()

config = Config()
logger.info("Configuration loaded", 
    host=config.connection.host,
    protocol=config.connection.protocol,
    pool_size=config.performance.connection_pool_size
)
```

### Environment Variables Not Working

1. Check variable names (use double underscore for nesting)
2. Ensure variables are exported
3. Check for typos in variable names
4. Verify `.env` file is in the working directory

## Next Steps

- [Basic Usage](basic-usage.md) - Start using the configured client
- [Performance Tuning](performance.md) - Optimize for your workload
- [Security Guide](security.md) - Secure your configuration
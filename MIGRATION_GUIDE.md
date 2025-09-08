# Migration Guide: v0.1.0 to v2.0.0

This guide helps you migrate from CMS-NBI-Client v0.1.0 to v2.0.0.

## Overview

Version 2.0.0 is a complete modernization of the CMS-NBI-Client with significant improvements in security, performance, and developer experience. While we've maintained backward compatibility where possible, some breaking changes were necessary.

## Breaking Changes

### 1. Python Version
- **Old**: Python 3.6+
- **New**: Python 3.9+ required

### 2. Configuration
- **Old**: Dictionary-based configuration
```python
# Old way
client = Client()
client.cmslogin("username", "password", "cms.example.com")
```

- **New**: Pydantic-based configuration
```python
# New way
from cmsnbiclient import CMSClient, Config

config = Config(
    credentials={"username": "user", "password": "pass"},
    connection={"host": "cms.example.com"}
)
client = CMSClient(config)
```

### 3. Async by Default
- **Old**: Synchronous operations only
```python
# Old way
result = client.E7.query.query_ont(network_name="NTWK-1", ont_id="123")
```

- **New**: Async operations (with sync wrapper available)
```python
# New async way
async with CMSClient(config) as client:
    result = await client.e7.query_ont(network_name="NTWK-1", ont_id="123")

# Sync wrapper for compatibility
with CMSClient.sync(config) as client:
    result = client.e7.query_ont(network_name="NTWK-1", ont_id="123")
```

### 4. Module Structure
- **Old**: `client.E7.create`, `client.E7.query`, etc.
- **New**: `client.e7.create_ont()`, `client.e7.query_ont()`, etc. (flattened structure)

### 5. HTTPS Default
- **Old**: HTTP only
- **New**: HTTPS by default (configurable)

## Step-by-Step Migration

### Step 1: Update Python Version
Ensure you're running Python 3.9 or later:
```bash
python --version  # Should show 3.9.0 or higher
```

### Step 2: Update Dependencies
```bash
pip uninstall cms-nbi-client
pip install cms-nbi-client>=2.0.0
```

### Step 3: Update Imports
```python
# Old
from cmsnbiclient import Client

# New
from cmsnbiclient import CMSClient, Config
```

### Step 4: Update Configuration
```python
# Old
client = Client()
client.cmslogin(username, password, ipaddress)

# New
config = Config(
    credentials={"username": username, "password": password},
    connection={"host": ipaddress, "protocol": "http"}  # Use http if needed
)
```

### Step 5: Update Client Usage

For minimal changes, use the sync wrapper:
```python
# Old
client = Client()
client.cmslogin(username, password, ipaddress)
result = client.E7.query.query_ont(network_name="NTWK-1", ont_id="123")

# New (minimal change - using sync wrapper)
config = Config(
    credentials={"username": username, "password": password},
    connection={"host": ipaddress}
)
with CMSClient.sync(config) as client:
    result = client.e7.query_ont(network_name="NTWK-1", ont_id="123")
```

For better performance, migrate to async:
```python
# New (async - recommended)
import asyncio

async def main():
    config = Config(
        credentials={"username": username, "password": password},
        connection={"host": ipaddress}
    )
    async with CMSClient(config) as client:
        result = await client.e7.query_ont(network_name="NTWK-1", ont_id="123")
    return result

result = asyncio.run(main())
```

### Step 6: Update Method Calls

The method structure has been flattened:
```python
# Old
client.E7.create.create_ont(...)
client.E7.query.query_ont(...)
client.E7.delete.delete_ont(...)
client.E7.update.update_ont(...)

# New
client.e7.create_ont(...)
client.e7.query_ont(...)
client.e7.delete_ont(...)
client.e7.update_ont(...)
```

### Step 7: Handle HTTPS
If your CMS doesn't support HTTPS:
```python
config = Config(
    credentials={"username": username, "password": password},
    connection={
        "host": ipaddress,
        "protocol": "http",  # Force HTTP
        "verify_ssl": False  # Disable SSL verification
    }
)
```

## New Features to Leverage

### 1. Connection Pooling
```python
config = Config(
    # ... credentials ...
    performance={
        "connection_pool_size": 100,
        "max_concurrent_requests": 50
    }
)
```

### 2. Structured Logging
```python
from cmsnbiclient import setup_logging
setup_logging(log_level="DEBUG", json_logs=False)
```

### 3. Concurrent Operations
```python
async with CMSClient(config) as client:
    # Create 100 ONTs concurrently
    tasks = [
        client.e7.create_ont(network_name="NTWK-1", ont_id=str(i))
        for i in range(100)
    ]
    results = await asyncio.gather(*tasks)
```

### 4. Environment Variables
```bash
export CMS_USERNAME=your_username
export CMS_PASSWORD=your_password
export CMS_CONNECTION__HOST=cms.example.com

# In Python
config = Config()  # Automatically loads from env
```

## Troubleshooting

### Issue: "Module 'Client' not found"
**Solution**: Update imports to use `CMSClient` instead of `Client`

### Issue: "HTTPS connection failed"
**Solution**: Either configure your CMS for HTTPS or use HTTP protocol in config

### Issue: "Async syntax error"
**Solution**: Use the sync wrapper or update your code to use async/await

### Issue: "Configuration validation error"
**Solution**: Ensure all required fields are provided in the Config object

## Need Help?

- Check the [examples](./Examples) directory for working code
- Review the [API documentation](./docs/api.md)
- Open an issue on [GitHub](https://github.com/somenetworking/CMS-NBI-Client/issues)

## Legacy Support

If you need to maintain compatibility with old code, you can use the legacy client:
```python
from cmsnbiclient import LegacyClient as Client
# Use as before (not recommended for new code)
```

Note: The legacy client is deprecated and will be removed in v3.0.0.
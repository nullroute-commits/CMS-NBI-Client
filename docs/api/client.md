# Client API Reference

::: cmsnbiclient.client_v2.CMSClient
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2
      members_order: source
      show_signature_annotations: true
      separate_signature: true
      line_length: 80

## Synchronous Client

::: cmsnbiclient.client_v2.SyncCMSClient
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2
      members_order: source
      show_signature_annotations: true
      separate_signature: true

## Usage Examples

### Async Client Usage

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    # Configure client
    config = Config(
        credentials={
            "username": "admin",
            "password": "secret"
        },
        connection={
            "host": "cms.example.com"
        }
    )
    
    # Use as async context manager
    async with CMSClient(config) as client:
        # Perform operations
        ont = await client.e7.query_ont(
            network_name="NTWK-1",
            ont_id="12345"
        )
        print(ont)

# Run async function
asyncio.run(main())
```

### Sync Client Usage

```python
from cmsnbiclient import CMSClient, Config

# Configure client
config = Config(
    credentials={
        "username": "admin",
        "password": "secret"
    },
    connection={
        "host": "cms.example.com"
    }
)

# Use sync wrapper
with CMSClient.sync(config) as client:
    # All operations work without await
    ont = client.e7.query_ont(
        network_name="NTWK-1",
        ont_id="12345"
    )
    print(ont)
```

### Manual Session Management

```python
# For cases where context manager isn't suitable
client = CMSClient(config)

try:
    # Manual authentication
    await client.authenticate()
    
    # Perform operations
    result = await client.e7.query_ont(
        network_name="NTWK-1",
        ont_id="12345"
    )
    
finally:
    # Always close when done
    await client.close()
```

### Error Handling

```python
from cmsnbiclient.exceptions import (
    AuthenticationError,
    ConnectionError,
    OperationError
)

async with CMSClient(config) as client:
    try:
        result = await client.e7.create_ont(
            network_name="NTWK-1",
            ont_id="12345",
            admin_state="enabled"
        )
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except OperationError as e:
        print(f"Operation failed: {e}")
```

### Concurrent Operations

```python
import asyncio

async with CMSClient(config) as client:
    # Create multiple ONTs concurrently
    tasks = []
    for i in range(100):
        task = client.e7.create_ont(
            network_name="NTWK-1",
            ont_id=str(i),
            admin_state="enabled"
        )
        tasks.append(task)
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"ONT {i} failed: {result}")
        else:
            print(f"ONT {i} created successfully")
```

## Client Attributes

### config

The configuration object passed during initialization:

```python
client = CMSClient(config)
print(client.config.connection.host)
print(client.config.performance.cache_ttl)
```

### e7

E7 operations handler:

```python
# Access E7-specific operations
await client.e7.create_ont(...)
await client.e7.query_ont(...)
await client.e7.update_ont(...)
await client.e7.delete_ont(...)
```

### rest

REST operations handler:

```python
# Access REST API operations
await client.rest.get_devices()
await client.rest.get_device_info(device_id="123")
```

### logger

Structured logger instance:

```python
# Log additional context
client.logger.info("Custom operation", 
    operation="bulk_create",
    count=100
)
```

## Advanced Usage

### Custom Transport

```python
from cmsnbiclient.core.transport import AsyncHTTPTransport

# Create custom transport
transport = AsyncHTTPTransport(config)

# Configure custom settings
transport._session.headers.update({
    "X-Custom-Header": "value"
})

# Use with client
client._transport = transport
```

### Session Reuse

```python
# Keep client alive for multiple operations
client = CMSClient(config)
await client.authenticate()

# Reuse session for multiple operations
for network in ["NTWK-1", "NTWK-2", "NTWK-3"]:
    onts = await client.e7.query_ont(network_name=network)
    print(f"{network}: {len(onts)} ONTs")

# Close when done
await client.close()
```

### Performance Monitoring

```python
import time

async with CMSClient(config) as client:
    start = time.time()
    
    # Perform operation
    result = await client.e7.query_ont(
        network_name="NTWK-1"
    )
    
    duration = time.time() - start
    client.logger.info("Query completed",
        duration=duration,
        result_count=len(result)
    )
```

## See Also

- [Configuration API](config.md) - Configuration options
- [E7 Operations API](e7.md) - E7-specific operations
- [REST Operations API](rest.md) - REST API operations
- [Base Classes](core.md) - Core components
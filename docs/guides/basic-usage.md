# Basic Usage Guide

!!! warning "Legacy-focused examples"
    The snippets below describe the planned E7/NETCONF API and reference `client.e7.*`. The modern `CMSClient` in this repository **does not** expose an `e7` attribute. Use the legacy `Client` together with `cmsnbiclient.E7.E7Operations` for NETCONF operations, or see the Quickstart for the current REST helper example.

This guide covers common usage patterns and operations with CMS-NBI-Client.

## Client Lifecycle

### Using Context Manager (Recommended)

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"}
    )
    
    # Automatic authentication and cleanup
    async with CMSClient(config) as client:
        # Client is authenticated and ready
        result = await client.e7.query_ont(network_name="NTWK-1")
        # Client automatically closes on exit

asyncio.run(main())
```

### Manual Lifecycle Management

```python
# For cases where context manager isn't suitable
client = CMSClient(config)

try:
    await client.authenticate()
    # Use client
    result = await client.e7.query_ont(network_name="NTWK-1")
finally:
    await client.close()
```

## Common Operations

### Query Operations

Query operations retrieve information without modifying data:

```python
async with CMSClient(config) as client:
    # Query all ONTs
    all_onts = await client.e7.query_ont(network_name="NTWK-1")
    
    # Query specific ONT
    ont = await client.e7.query_ont(
        network_name="NTWK-1",
        ont_id="12345"
    )
    
    # Query VLANs
    vlans = await client.e7.query_vlan(network_name="NTWK-1")
    
    # Query system information
    sys_info = await client.e7.query_system_info(network_name="NTWK-1")
```

### Create Operations

Create new resources in the CMS:

```python
async with CMSClient(config) as client:
    # Create ONT
    ont_result = await client.e7.create_ont(
        network_name="NTWK-1",
        ont_id="67890",
        admin_state="enabled",
        ont_profile_id="1",
        serial_number="CXNK12345678",
        description="Customer John Doe"
    )
    
    # Create VLAN
    vlan_result = await client.e7.create_vlan(
        network_name="NTWK-1",
        vlan_id="100",
        name="Customer_VLAN",
        description="Customer service VLAN"
    )
    
    # Add VLAN member
    member_result = await client.e7.create_vlan_member(
        network_name="NTWK-1",
        vlan_id="100",
        ont_id="67890",
        port="g1",
        tagged=False
    )
```

### Update Operations

Modify existing resources:

```python
async with CMSClient(config) as client:
    # Update ONT state
    result = await client.e7.update_ont(
        network_name="NTWK-1",
        ont_id="12345",
        admin_state="disabled"
    )
    
    # Update ONT description
    result = await client.e7.update_ont(
        network_name="NTWK-1",
        ont_id="12345",
        description="Maintenance window"
    )
    
    # Update multiple fields
    result = await client.e7.update_ont(
        network_name="NTWK-1",
        ont_id="12345",
        admin_state="enabled",
        description="Service restored",
        subscriber_id="NEW_SUB_123"
    )
```

### Delete Operations

Remove resources from the CMS:

```python
async with CMSClient(config) as client:
    # Delete ONT
    result = await client.e7.delete_ont(
        network_name="NTWK-1",
        ont_id="67890"
    )
    
    # Delete VLAN member
    result = await client.e7.delete_vlan_member(
        network_name="NTWK-1",
        vlan_id="100",
        ont_id="67890",
        port="g1"
    )
    
    # Delete VLAN
    result = await client.e7.delete_vlan(
        network_name="NTWK-1",
        vlan_id="100"
    )
```

## Working with Results

### Understanding Response Format

```python
async with CMSClient(config) as client:
    # Single resource query
    ont = await client.e7.query_ont(
        network_name="NTWK-1",
        ont_id="12345"
    )
    # Returns dict with ONT properties
    print(f"ONT ID: {ont.get('ont_id')}")
    print(f"Status: {ont.get('admin_state')}")
    print(f"Serial: {ont.get('serial_number')}")
    
    # Multiple resource query
    all_onts = await client.e7.query_ont(network_name="NTWK-1")
    # Returns list of dicts
    for ont in all_onts:
        print(f"ONT {ont.get('ont_id')}: {ont.get('admin_state')}")
```

### Checking Operation Success

```python
async with CMSClient(config) as client:
    try:
        result = await client.e7.create_ont(
            network_name="NTWK-1",
            ont_id="99999",
            admin_state="enabled",
            ont_profile_id="1"
        )
        
        # Check result
        if result.get('status') == 'success':
            print("ONT created successfully")
        else:
            print(f"Creation failed: {result.get('error')}")
            
    except OperationError as e:
        print(f"Operation failed: {e}")
```

## Error Handling

### Basic Error Handling

```python
from cmsnbiclient.exceptions import (
    AuthenticationError,
    ConnectionError,
    OperationError
)

async with CMSClient(config) as client:
    try:
        result = await client.e7.query_ont(
            network_name="NTWK-1",
            ont_id="12345"
        )
    except AuthenticationError:
        print("Failed to authenticate")
    except ConnectionError:
        print("Network connection failed")
    except OperationError as e:
        print(f"Operation failed: {e}")
```

### Handling Specific Errors

```python
async def create_ont_safe(client, ont_id):
    """Create ONT with proper error handling"""
    try:
        result = await client.e7.create_ont(
            network_name="NTWK-1",
            ont_id=ont_id,
            admin_state="enabled",
            ont_profile_id="1"
        )
        return True, result
        
    except OperationError as e:
        error_msg = str(e).lower()
        
        if "already exists" in error_msg:
            print(f"ONT {ont_id} already exists")
            return False, "exists"
            
        elif "invalid ont_id" in error_msg:
            print(f"Invalid ONT ID: {ont_id}")
            return False, "invalid"
            
        else:
            print(f"Unexpected error: {e}")
            return False, "error"
```

## Batch Operations

### Processing Multiple Items

```python
async def process_ont_list(client, ont_ids):
    """Process a list of ONTs"""
    results = {
        "success": [],
        "failed": []
    }
    
    for ont_id in ont_ids:
        try:
            result = await client.e7.create_ont(
                network_name="NTWK-1",
                ont_id=ont_id,
                admin_state="enabled",
                ont_profile_id="1"
            )
            results["success"].append(ont_id)
            
        except Exception as e:
            results["failed"].append({
                "ont_id": ont_id,
                "error": str(e)
            })
    
    return results
```

### Concurrent Batch Operations

```python
import asyncio

async def concurrent_batch_create(client, ont_configs):
    """Create multiple ONTs concurrently"""
    
    async def create_single(config):
        try:
            return await client.e7.create_ont(
                network_name="NTWK-1",
                **config
            )
        except Exception as e:
            return {"error": str(e), "config": config}
    
    # Create all concurrently
    tasks = [create_single(config) for config in ont_configs]
    results = await asyncio.gather(*tasks)
    
    # Separate successes and failures
    successes = [r for r in results if "error" not in r]
    failures = [r for r in results if "error" in r]
    
    return {
        "created": len(successes),
        "failed": len(failures),
        "failures": failures
    }
```

## Working with Multiple Networks

```python
async def multi_network_operations(client):
    """Perform operations across multiple networks"""
    networks = ["NTWK-1", "NTWK-2", "NTWK-3"]
    
    all_results = {}
    
    for network in networks:
        try:
            # Query ONTs in each network
            onts = await client.e7.query_ont(network_name=network)
            all_results[network] = {
                "ont_count": len(onts),
                "enabled": sum(1 for o in onts if o.get('admin_state') == 'enabled'),
                "disabled": sum(1 for o in onts if o.get('admin_state') == 'disabled')
            }
        except Exception as e:
            all_results[network] = {"error": str(e)}
    
    return all_results
```

## Filtering and Searching

```python
async def find_onts_by_criteria(client, network_name):
    """Find ONTs matching specific criteria"""
    
    # Get all ONTs
    all_onts = await client.e7.query_ont(network_name=network_name)
    
    # Filter by admin state
    enabled_onts = [
        ont for ont in all_onts 
        if ont.get('admin_state') == 'enabled'
    ]
    
    # Filter by description pattern
    customer_onts = [
        ont for ont in all_onts 
        if 'customer' in ont.get('description', '').lower()
    ]
    
    # Filter by serial number prefix
    cxnk_onts = [
        ont for ont in all_onts 
        if ont.get('serial_number', '').startswith('CXNK')
    ]
    
    # Complex filtering
    problem_onts = [
        ont for ont in all_onts 
        if (ont.get('admin_state') == 'enabled' and 
            'problem' in ont.get('description', '').lower())
    ]
    
    return {
        "total": len(all_onts),
        "enabled": len(enabled_onts),
        "customer": len(customer_onts),
        "cxnk_serial": len(cxnk_onts),
        "problems": problem_onts
    }
```

## Logging and Debugging

### Enable Debug Logging

```python
from cmsnbiclient import setup_logging

# Enable debug logging
setup_logging(log_level="DEBUG", json_logs=False)

# Your operations will now show detailed logs
async with CMSClient(config) as client:
    result = await client.e7.query_ont(network_name="NTWK-1")
```

### Custom Logging

```python
import structlog

logger = structlog.get_logger()

async def operation_with_logging(client):
    logger.info("Starting operation", network="NTWK-1")
    
    try:
        result = await client.e7.query_ont(network_name="NTWK-1")
        logger.info("Operation successful", ont_count=len(result))
        return result
        
    except Exception as e:
        logger.error("Operation failed", error=str(e))
        raise
```

## Performance Tips

### 1. Use Connection Pooling

```python
config = Config(
    performance={
        "connection_pool_size": 200,  # Increase for high load
        "max_concurrent_requests": 100
    }
)
```

### 2. Enable Caching for Read Operations

```python
config = Config(
    performance={
        "cache_ttl": 600  # 10-minute cache
    }
)

# First query hits network
onts1 = await client.e7.query_ont(network_name="NTWK-1")

# Subsequent queries use cache
onts2 = await client.e7.query_ont(network_name="NTWK-1")  # From cache
```

### 3. Batch Operations

Instead of:
```python
# Slow - sequential
for ont_id in ont_ids:
    await client.e7.create_ont(network_name="NTWK-1", ont_id=ont_id, ...)
```

Do:
```python
# Fast - concurrent
tasks = [
    client.e7.create_ont(network_name="NTWK-1", ont_id=ont_id, ...)
    for ont_id in ont_ids
]
results = await asyncio.gather(*tasks)
```

## Next Steps

- [Async Operations Guide](async-operations.md) - Advanced async patterns
- [Error Handling Guide](error-handling.md) - Comprehensive error handling
- [Performance Tuning](performance.md) - Optimize for your use case
- [API Reference](../api/client.md) - Complete API documentation

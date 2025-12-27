# E7 Operations Examples

!!! warning "Requires legacy client"
    The modern `CMSClient` does not expose `e7` operations. Use the legacy `Client` plus `cmsnbiclient.E7.E7Operations` after calling `login_netconf` to run these examples.

This guide provides practical examples of E7 operations using CMS-NBI-Client.

## ONT Operations

### Query ONTs

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def query_ont_examples():
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"}
    )
    
    async with CMSClient(config) as client:
        # Query all ONTs in a network
        all_onts = await client.e7.query_ont(network_name="NTWK-1")
        print(f"Total ONTs: {len(all_onts)}")
        
        # Query specific ONT
        ont = await client.e7.query_ont(
            network_name="NTWK-1",
            ont_id="12345"
        )
        print(f"ONT 12345 Status: {ont.get('admin_state')}")
        
        # Query with filtering (if supported)
        enabled_onts = [
            ont for ont in all_onts 
            if ont.get('admin_state') == 'enabled'
        ]
        print(f"Enabled ONTs: {len(enabled_onts)}")

asyncio.run(query_ont_examples())
```

### Create ONT

```python
async def create_ont_example():
    async with CMSClient(config) as client:
        # Basic ONT creation
        result = await client.e7.create_ont(
            network_name="NTWK-1",
            ont_id="67890",
            admin_state="enabled",
            ont_profile_id="1"
        )
        print(f"ONT created: {result}")
        
        # Create with full parameters
        result = await client.e7.create_ont(
            network_name="NTWK-1",
            ont_id="67891",
            admin_state="enabled",
            ont_profile_id="1",
            serial_number="CXNK12345678",
            registration_id="REG123",
            subscriber_id="SUB123",
            description="Customer John Doe",
            battery_present=True
        )
        print(f"ONT created with details: {result}")
```

### Update ONT

```python
async def update_ont_example():
    async with CMSClient(config) as client:
        # Update admin state
        result = await client.e7.update_ont(
            network_name="NTWK-1",
            ont_id="12345",
            admin_state="disabled"
        )
        print(f"ONT disabled: {result}")
        
        # Update description
        result = await client.e7.update_ont(
            network_name="NTWK-1",
            ont_id="12345",
            description="Updated: Maintenance required"
        )
        
        # Update multiple fields
        result = await client.e7.update_ont(
            network_name="NTWK-1",
            ont_id="12345",
            admin_state="enabled",
            description="Maintenance completed",
            subscriber_id="NEW_SUB_123"
        )
```

### Delete ONT

```python
async def delete_ont_example():
    async with CMSClient(config) as client:
        # Delete single ONT
        result = await client.e7.delete_ont(
            network_name="NTWK-1",
            ont_id="67890"
        )
        print(f"ONT deleted: {result}")
        
        # Delete multiple ONTs
        ont_ids = ["67891", "67892", "67893"]
        for ont_id in ont_ids:
            try:
                result = await client.e7.delete_ont(
                    network_name="NTWK-1",
                    ont_id=ont_id
                )
                print(f"Deleted ONT {ont_id}")
            except Exception as e:
                print(f"Failed to delete ONT {ont_id}: {e}")
```

## VLAN Operations

### Create VLAN

```python
async def create_vlan_example():
    async with CMSClient(config) as client:
        # Create customer VLAN
        result = await client.e7.create_vlan(
            network_name="NTWK-1",
            vlan_id="100",
            name="Customer_VLAN_100",
            description="Customer ABC Internet Service"
        )
        print(f"VLAN created: {result}")
        
        # Create management VLAN
        result = await client.e7.create_vlan(
            network_name="NTWK-1",
            vlan_id="4000",
            name="MGMT_VLAN",
            description="Management VLAN"
        )
```

### Add VLAN Members

```python
async def add_vlan_members_example():
    async with CMSClient(config) as client:
        # Add ONT port to VLAN
        result = await client.e7.create_vlan_member(
            network_name="NTWK-1",
            vlan_id="100",
            ont_id="12345",
            port="g1",  # Gigabit port 1
            tagged=False  # Untagged
        )
        print(f"VLAN member added: {result}")
        
        # Add multiple ports
        ports = ["g1", "g2", "g3", "g4"]
        for port in ports:
            result = await client.e7.create_vlan_member(
                network_name="NTWK-1",
                vlan_id="100",
                ont_id="12345",
                port=port,
                tagged=True  # Tagged
            )
```

### Query VLANs

```python
async def query_vlan_example():
    async with CMSClient(config) as client:
        # Query all VLANs
        vlans = await client.e7.query_vlan(network_name="NTWK-1")
        print(f"Total VLANs: {len(vlans)}")
        
        # Query specific VLAN
        vlan = await client.e7.query_vlan(
            network_name="NTWK-1",
            vlan_id="100"
        )
        print(f"VLAN 100: {vlan}")
        
        # Query VLAN members
        members = await client.e7.query_vlan_members(
            network_name="NTWK-1",
            vlan_id="100"
        )
        print(f"VLAN 100 has {len(members)} members")
```

## Ethernet Service Operations

### Create Ethernet Service

```python
async def create_eth_service_example():
    async with CMSClient(config) as client:
        # Create point-to-point service
        result = await client.e7.create_eth_service(
            network_name="NTWK-1",
            service_name="ETH_SVC_001",
            service_type="epl",  # Ethernet Private Line
            ont_id="12345",
            port="g1",
            vlan_id="100",
            bandwidth="100M"
        )
        print(f"Ethernet service created: {result}")
```

## DHCP Operations

### Query DHCP Leases

```python
async def query_dhcp_leases_example():
    async with CMSClient(config) as client:
        # Query all DHCP leases for an ONT
        leases = await client.e7.query_dhcp_leases(
            network_name="NTWK-1",
            ont_id="12345"
        )
        
        for lease in leases:
            print(f"IP: {lease.get('ip_address')}")
            print(f"MAC: {lease.get('mac_address')}")
            print(f"Hostname: {lease.get('hostname')}")
            print(f"Expires: {lease.get('expiry_time')}")
            print("---")
```

## Bulk Operations

### Bulk ONT Creation

```python
async def bulk_create_onts():
    async with CMSClient(config) as client:
        # Prepare ONT data
        ont_configs = [
            {
                "ont_id": str(1000 + i),
                "admin_state": "enabled",
                "ont_profile_id": "1",
                "description": f"Bulk ONT {i}"
            }
            for i in range(100)
        ]
        
        # Create concurrently with limited concurrency
        import asyncio
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent
        
        async def create_with_limit(config):
            async with semaphore:
                return await client.e7.create_ont(
                    network_name="NTWK-1",
                    **config
                )
        
        # Execute all
        tasks = [create_with_limit(config) for config in ont_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"Created {successes} ONTs, {failures} failed")
```

### Bulk Status Update

```python
async def bulk_disable_onts():
    async with CMSClient(config) as client:
        # Get all ONTs
        all_onts = await client.e7.query_ont(network_name="NTWK-1")
        
        # Filter ONTs to disable
        onts_to_disable = [
            ont for ont in all_onts
            if ont.get('admin_state') == 'enabled' and 
            ont.get('description', '').startswith('TEST_')
        ]
        
        print(f"Disabling {len(onts_to_disable)} test ONTs...")
        
        # Disable them
        for ont in onts_to_disable:
            try:
                await client.e7.update_ont(
                    network_name="NTWK-1",
                    ont_id=ont['ont_id'],
                    admin_state="disabled"
                )
                print(f"Disabled ONT {ont['ont_id']}")
            except Exception as e:
                print(f"Failed to disable ONT {ont['ont_id']}: {e}")
```

## Error Handling

### Comprehensive Error Handling

```python
from cmsnbiclient.exceptions import (
    AuthenticationError,
    OperationError,
    ConnectionError,
    ValidationError
)

async def robust_operation():
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"}
    )
    
    try:
        async with CMSClient(config) as client:
            # Attempt operation
            result = await client.e7.create_ont(
                network_name="NTWK-1",
                ont_id="99999",
                admin_state="enabled",
                ont_profile_id="1"
            )
            print(f"Success: {result}")
            
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle auth failure (maybe refresh credentials)
        
    except ValidationError as e:
        print(f"Invalid parameters: {e}")
        # Handle validation errors
        
    except OperationError as e:
        print(f"Operation failed: {e}")
        # Check if ONT already exists, etc.
        
    except ConnectionError as e:
        print(f"Connection failed: {e}")
        # Handle network issues
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unknown errors

asyncio.run(robust_operation())
```

## Performance Optimization

### Caching Queries

```python
async def cached_queries():
    # Configure with caching
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"},
        performance={"cache_ttl": 600}  # 10-minute cache
    )
    
    async with CMSClient(config) as client:
        # First query hits the network
        start = time.time()
        onts1 = await client.e7.query_ont(network_name="NTWK-1")
        print(f"First query: {time.time() - start:.2f}s")
        
        # Second query uses cache
        start = time.time()
        onts2 = await client.e7.query_ont(network_name="NTWK-1")
        print(f"Cached query: {time.time() - start:.2f}s")
```

### Connection Pooling

```python
async def connection_pool_example():
    # Configure for high concurrency
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"},
        performance={
            "connection_pool_size": 200,
            "max_concurrent_requests": 100
        }
    )
    
    async with CMSClient(config) as client:
        # Many concurrent operations will reuse connections
        tasks = []
        for i in range(100):
            task = client.e7.query_ont(
                network_name="NTWK-1",
                ont_id=str(i)
            )
            tasks.append(task)
        
        # Execute all concurrently
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} queries")
```

## Best Practices

1. **Always use context managers** - Ensures proper cleanup
2. **Handle exceptions** - Especially for bulk operations
3. **Use appropriate timeouts** - Don't wait forever
4. **Limit concurrency** - Respect server limits
5. **Cache when appropriate** - Reduce unnecessary queries
6. **Log operations** - For debugging and auditing

## Next Steps

- [REST Operations Examples](rest-operations.md)
- [Concurrent Operations](concurrent.md)
- [Error Recovery Patterns](error-recovery.md)

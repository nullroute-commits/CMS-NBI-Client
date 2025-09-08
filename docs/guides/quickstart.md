# Quick Start Guide

Get up and running with CMS-NBI-Client in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Access to a CMS instance
- CMS credentials (username/password)

## Installation

```bash
pip install cms-nbi-client
```

## Your First Script

### 1. Basic Connection

Create a file `first_script.py`:

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    # Configure the client
    config = Config(
        credentials={
            "username": "your_username",
            "password": "your_password"
        },
        connection={
            "host": "cms.example.com",
            "protocol": "https"  # or "http" if needed
        }
    )
    
    # Connect and query an ONT
    async with CMSClient(config) as client:
        # Query ONT information
        ont_info = await client.e7.query_ont(
            network_name="NTWK-1",
            ont_id="12345"
        )
        
        print(f"ONT Status: {ont_info.get('admin_state')}")
        print(f"Serial Number: {ont_info.get('serial_number')}")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Run the Script

```bash
python first_script.py
```

## Common Operations

### Query Operations

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
    
    # Query DHCP leases
    leases = await client.e7.query_dhcp_leases(
        network_name="NTWK-1",
        ont_id="12345"
    )
```

### Create Operations

```python
async with CMSClient(config) as client:
    # Create an ONT
    result = await client.e7.create_ont(
        network_name="NTWK-1",
        ont_id="67890",
        admin_state="enabled",
        ont_profile_id="1",
        serial_number="CXNK12345678"
    )
    
    # Create a VLAN
    vlan_result = await client.e7.create_vlan(
        network_name="NTWK-1",
        vlan_id="100",
        name="Customer_VLAN_100"
    )
```

### Update Operations

```python
async with CMSClient(config) as client:
    # Update ONT admin state
    result = await client.e7.update_ont(
        network_name="NTWK-1",
        ont_id="12345",
        admin_state="disabled"
    )
    
    # Update ONT description
    result = await client.e7.update_ont(
        network_name="NTWK-1",
        ont_id="12345",
        description="Updated description"
    )
```

### Delete Operations

```python
async with CMSClient(config) as client:
    # Delete an ONT
    result = await client.e7.delete_ont(
        network_name="NTWK-1",
        ont_id="67890"
    )
    
    # Delete a VLAN
    vlan_result = await client.e7.delete_vlan(
        network_name="NTWK-1",
        vlan_id="100"
    )
```

## Error Handling

Always handle potential errors:

```python
import asyncio
from cmsnbiclient import CMSClient, Config
from cmsnbiclient.exceptions import (
    AuthenticationError,
    OperationError,
    ConnectionError
)

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
    
    try:
        async with CMSClient(config) as client:
            ont = await client.e7.query_ont(
                network_name="NTWK-1",
                ont_id="12345"
            )
            print(f"ONT found: {ont}")
            
    except AuthenticationError:
        print("Failed to authenticate with CMS")
    except ConnectionError:
        print("Failed to connect to CMS")
    except OperationError as e:
        print(f"Operation failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Synchronous Usage

If you can't use async/await, use the sync wrapper:

```python
from cmsnbiclient import CMSClient, Config

# Configure
config = Config(
    credentials={
        "username": "your_username",
        "password": "your_password"
    },
    connection={
        "host": "cms.example.com"
    }
)

# Use sync client
with CMSClient.sync(config) as client:
    # All operations work the same, just without await
    ont = client.e7.query_ont(
        network_name="NTWK-1",
        ont_id="12345"
    )
    print(f"ONT Status: {ont.get('admin_state')}")
```

## Environment Variables

Instead of hardcoding credentials:

```bash
# Set environment variables
export CMS_USERNAME=your_username
export CMS_PASSWORD=your_password
export CMS_CONNECTION__HOST=cms.example.com
```

Then in your script:

```python
from cmsnbiclient import CMSClient, Config

# Config automatically loads from environment
config = Config()

async with CMSClient(config) as client:
    # Use client as normal
    pass
```

## Configuration File

Create `config.yaml`:

```yaml
credentials:
  username: your_username
  password: your_password
  
connection:
  host: cms.example.com
  protocol: https
  verify_ssl: true
  
performance:
  connection_pool_size: 100
  cache_ttl: 300
```

Load in your script:

```python
from pathlib import Path
from cmsnbiclient import CMSClient, Config

config = Config.from_file(Path("config.yaml"))

async with CMSClient(config) as client:
    # Use client
    pass
```

## Logging

Enable detailed logging for debugging:

```python
from cmsnbiclient import setup_logging

# Enable debug logging
setup_logging(log_level="DEBUG", json_logs=False)

# Your code here...
```

## Next Steps

Now that you have the basics:

1. **[Configuration Guide](configuration.md)** - Learn about all configuration options
2. **[Basic Usage Guide](basic-usage.md)** - Explore more operations
3. **[Async Operations Guide](async-operations.md)** - Master async patterns
4. **[API Reference](../api/client.md)** - Detailed API documentation

## Getting Help

- Check the [FAQ](faq.md)
- Browse [Examples](../examples/e7-operations.md)
- Open an [issue on GitHub](https://github.com/somenetworking/CMS-NBI-Client/issues)
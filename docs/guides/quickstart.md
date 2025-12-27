# Quick Start Guide

Get up and running with the **current** CMS-NBI-Client behavior in 5 minutes.

!!! warning "Feature availability"
    The modern `CMSClient` handles configuration, authentication, and synchronous REST helper calls. NETCONF/E7 operations are only available through the legacy `Client` + `E7Operations` classes. The `CMSClient` **does not** expose an `e7` attribute today.

## Prerequisites

- Python 3.9+ installed
- Access to a CMS instance
- CMS credentials (username/password)

## Installation

```bash
pip install cms-nbi-client
```

## Your First Script (CMSClient + REST devices)

Create `first_script.py`:

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    config = Config(
        credentials={"username": "your_username", "password": "your_password"},
        connection={"host": "cms.example.com", "protocol": "https"},
    )

    async with CMSClient(config) as client:
        # REST helper calls are synchronous
        devices = client.rest.query_devices(
            cms_user_nm=config.credentials.username,
            cms_user_pass=config.credentials.password.get_secret_value(),
            cms_node_ip=config.connection.host,
            device_type="e7",
            http_timeout=5,
        )
        print(devices)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python first_script.py
```

## Using legacy NETCONF/E7 operations

```python
from cmsnbiclient import LegacyClient
# Note: the E7 package name is capitalized in the module path
from cmsnbiclient.E7 import E7Operations

legacy = LegacyClient()
legacy.login_netconf(
    cms_user_nm="your_username",
    cms_user_pass="your_password",
    cms_node_ip="cms.example.com",
    uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"],
)

e7 = E7Operations(legacy)
result = e7.create.ont(network_nm="NTWK-1", ont_id="67890")
legacy.logout_netconf(uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"])
```

## Environment Variables

```bash
export CMS_USERNAME=your_username
export CMS_PASSWORD=your_password
export CMS_CONNECTION__HOST=cms.example.com
```

Then:

```python
from cmsnbiclient import CMSClient, Config

config = Config()  # loads from environment
```

## Configuration File

```yaml
credentials:
  username: your_username
  password: your_password

connection:
  host: cms.example.com
  protocol: https
  verify_ssl: true
```

```python
from pathlib import Path
from cmsnbiclient import CMSClient, Config

config = Config.from_file(Path("config.yaml"))
```

## Logging

```python
from cmsnbiclient import setup_logging

setup_logging(log_level="DEBUG", json_logs=False)
```

## Next Steps

1. **[Configuration Guide](configuration.md)**
2. **[API Reference](../api/client.md)**

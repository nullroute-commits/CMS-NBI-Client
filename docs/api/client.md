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

!!! warning "E7 operations not exposed on `CMSClient`"
    The async `CMSClient` only authenticates and exposes synchronous REST helpers through `client.rest`. NETCONF/E7 operations live in the legacy client (`cmsnbiclient.client.Client` + `cmsnbiclient.E7.E7Operations`).

### Async CMSClient + REST devices

```python
import asyncio
from cmsnbiclient import CMSClient, Config

async def main():
    config = Config(
        credentials={"username": "admin", "password": "secret"},
        connection={"host": "cms.example.com"},
    )

    async with CMSClient(config) as client:
        # REST helpers are synchronous today
        devices = client.rest.query_devices(
            cms_user_nm=config.credentials.username,
            cms_user_pass=config.credentials.password.get_secret_value(),
            cms_node_ip=config.connection.host,
            device_type="e7",
        )
        print(devices)

asyncio.run(main())
```

### Sync wrapper (lifecycle only)

`SyncCMSClient` sets up and tears down an internal `CMSClient`. Operations must be invoked on the underlying async client stored on `_client`.

```python
from cmsnbiclient import CMSClient, Config

config = Config(
    credentials={"username": "admin", "password": "secret"},
    connection={"host": "cms.example.com"},
)

with CMSClient.sync(config) as wrapper:
    devices = wrapper._client.rest.query_devices(  # synchronous REST call
        cms_user_nm=config.credentials.username,
        cms_user_pass=config.credentials.password.get_secret_value(),
        cms_node_ip=config.connection.host,
    )
    print(devices)
```

### Legacy NETCONF/E7 usage

```python
from cmsnbiclient import LegacyClient
from cmsnbiclient.E7 import E7Operations  # Package name is capitalized

legacy = LegacyClient()
legacy.login_netconf(
    cms_user_nm="admin",
    cms_user_pass="secret",
    cms_node_ip="cms.example.com",
    uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"],
)

e7 = E7Operations(legacy)
ont = e7.create.ont(network_nm="NTWK-1", ont_id="12345")
legacy.logout_netconf(uri=legacy.cms_nbi_config["cms_netconf_uri"]["e7"])
```

## Client Attributes

### config

The Pydantic configuration object passed during initialization:

```python
client = CMSClient(config)
print(client.config.connection.host)
print(client.config.performance.cache_ttl)
```

### rest

REST operations handler (methods are synchronous):

```python
devices = client.rest.query_devices(
    cms_user_nm=config.credentials.username,
    cms_user_pass=config.credentials.password.get_secret_value(),
    cms_node_ip=config.connection.host,
    device_type="e7",
)
```

### logger

Structured logger instance:

```python
client.logger.info("rest.devices", target_host=client.config.connection.host)
```

## Advanced Usage

### Custom Transport

```python
from cmsnbiclient.core.transport import AsyncHTTPTransport

transport = AsyncHTTPTransport(config)
client._transport = transport
```

### Session Reuse

```python
client = CMSClient(config)
await client.authenticate()

devices = client.rest.query_devices(
    cms_user_nm=config.credentials.username,
    cms_user_pass=config.credentials.password.get_secret_value(),
    cms_node_ip=config.connection.host,
)

await client.close()
```

## See Also

- [Configuration API](config.md) - Configuration options
- [Legacy E7 examples](../examples/e7-operations.md) - Requires `LegacyClient`
- [Base Classes](core.md) - Core components

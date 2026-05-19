import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Type, cast

import aiohttp
import structlog
from defusedxml import ElementTree as DefusedET

from .core.base import BaseClient
from .core.config import Config
from .core.transport import AsyncHTTPTransport
from .E7 import Create as E7Create
from .E7 import Delete as E7Delete
from .E7 import Query as E7Query
from .E7 import Update as E7Update
from .exceptions import AuthenticationError
from .REST import RESTOperations
from .security.credentials import SecureCredentialManager

logger = structlog.get_logger()


class _LegacyOperationGroup:
    """Compatibility wrapper that lazily instantiates legacy E7 operations."""

    def __init__(self, client: "CMSClient", factory: Type[Any]):
        self._client = client
        self._factory = factory

    def __getattr__(self, method_name: str) -> Callable[..., Any]:
        def caller(*args: Any, **kwargs: Any) -> Any:
            network_name = kwargs.pop("network_name", None) or kwargs.pop("network_nm", "")
            http_timeout = kwargs.pop("http_timeout", 1)
            operation = self._factory(
                self._client, network_nm=network_name, http_timeout=http_timeout
            )
            method = getattr(operation, method_name)
            return method(*args, **kwargs)

        return caller


class LegacyE7Facade:
    """Compatibility facade that preserves the documented `client.e7.*` surface."""

    def __init__(self, client: "CMSClient"):
        self.create = _LegacyOperationGroup(client, E7Create)
        self.delete = _LegacyOperationGroup(client, E7Delete)
        self.query = _LegacyOperationGroup(client, E7Query)
        self.update = _LegacyOperationGroup(client, E7Update)

    def __getattr__(self, name: str) -> Callable[..., Any]:
        for prefix, group in (
            ("create_", self.create),
            ("delete_", self.delete),
            ("query_", self.query),
            ("update_", self.update),
        ):
            if name.startswith(prefix):
                return cast(Callable[..., Any], getattr(group, name[len(prefix) :]))
        raise AttributeError(name)


class CMSClient(BaseClient):
    """Modern async CMS client with all features"""

    def __init__(self, config: Config):
        super().__init__(config)
        self._transport = AsyncHTTPTransport(config)
        self._credential_manager = SecureCredentialManager()
        self._auth_time: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()
        self.cms_nbi_config = self._build_legacy_compat_config()
        self.cms_netconf_url = self._build_netconf_url()
        self.session_id: Optional[str] = None
        self.cms_user_nm = config.credentials.username

        # Operation handlers
        self.e7 = LegacyE7Facade(self)
        self.rest = RESTOperations(self)

    async def authenticate(self) -> None:
        """Authenticate with CMS"""
        async with self._auth_lock:
            # Check if already authenticated
            if self._session_id and self._auth_time:
                if datetime.now() - self._auth_time < timedelta(hours=1):
                    return

            self.logger.info("Authenticating with CMS")

            # Get credentials
            username = self.config.credentials.username
            password = self.config.credentials.password.get_secret_value()

            # Build login payload
            payload = self._build_login_payload(username, password)

            # Send request
            url = self._build_netconf_url()
            if self._transport is None:
                raise RuntimeError("Transport not initialized")
            response = await self._transport.request(
                method="POST",
                url=url,
                data=payload,
                headers={"Content-Type": "text/xml;charset=ISO-8859-1"},
            )

            # Parse response
            result = await self._parse_auth_response(response)
            self._session_id = result["session_id"]
            self.session_id = result["session_id"]
            self._auth_time = datetime.now()

            self.logger.info("Authentication successful", session_id=self._session_id)

    async def close(self) -> None:
        """Close client and cleanup"""
        if self._session_id:
            try:
                await self._logout()
            except Exception as e:
                self.logger.error(f"Logout failed: {e}")

        if self._transport is not None and hasattr(self._transport, "close"):
            await self._transport.close()  # type: ignore

    async def _logout(self) -> None:
        """Logout from CMS"""
        payload = self._build_logout_payload()
        url = self._build_netconf_url()

        if self._transport is None:
            raise RuntimeError("Transport not initialized")
        response = await self._transport.request(
            method="POST",
            url=url,
            data=payload,
            headers={"Content-Type": "text/xml;charset=ISO-8859-1"},
        )
        await response.read()
        response.release()

        self._session_id = None
        self.session_id = None
        self.logger.info("Logged out successfully")

    def _build_netconf_url(self) -> str:
        """Build NETCONF URL"""
        return (
            f"{self.config.connection.protocol}://"
            f"{self.config.connection.host}:"
            f"{self.config.connection.netconf_port}"
            "/cmsexc/ex/netconf"
        )

    def _build_login_payload(self, username: str, password: str) -> str:
        """Build login XML payload"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <auth-req>
            <UserName>{username}</UserName>
            <Password>{password}</Password>
        </auth-req>
    </soapenv:Body>
</soapenv:Envelope>"""

    def _build_logout_payload(self) -> str:
        """Build logout XML payload"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <logout-req>
            <SessionId>{self._session_id}</SessionId>
        </logout-req>
    </soapenv:Body>
</soapenv:Envelope>"""

    def _build_legacy_compat_config(self) -> Dict[str, Any]:
        """Build minimal legacy-compatible configuration for shared modules."""
        return {
            "cms_netconf_uri": {
                "e7": "/cmsexc/ex/netconf",
                "c7/e3/e5-100": "/cmsweb/nc",
                "ae_ont": "/cmsae/ae/netconf",
            },
            "cms_rest_uri": {
                "devices": "/restnbi/devices?deviceType=",
                "region": "/restnbi/region",
                "topology": "/restnbi/toplinks",
                "profile": "/restnbi/profiles?profileType=",
            },
        }

    @staticmethod
    def _find_xml_text(root: Any, tag_name: str) -> Optional[str]:
        """Find an element value regardless of namespace prefix."""
        for element in root.iter():
            if isinstance(element.tag, str) and element.tag.split("}")[-1] == tag_name:
                if isinstance(element.text, str) and element.text:
                    return element.text.strip()
        return None

    async def _parse_auth_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse authentication response"""
        try:
            text = await response.text()
        finally:
            response.release()

        try:
            root = DefusedET.fromstring(text)
        except DefusedET.ParseError as exc:
            raise AuthenticationError("Authentication failed: invalid XML response") from exc

        result_code = self._find_xml_text(root, "ResultCode")
        session_id = self._find_xml_text(root, "SessionId")

        if result_code and result_code != "0":
            raise AuthenticationError(f"Authentication failed with result code {result_code}")
        if not session_id:
            raise AuthenticationError("Authentication failed: no session ID in response")
        return {"session_id": session_id}

    @classmethod
    def sync(cls, config: Config) -> "SyncCMSClient":
        """Create synchronous client wrapper"""
        return SyncCMSClient(config)


class SyncCMSClient:
    """Synchronous wrapper for async client"""

    def __init__(self, config: Config):
        self._config = config
        self._client: Optional[CMSClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def __enter__(self) -> "SyncCMSClient":
        self._loop = asyncio.new_event_loop()
        self._client = CMSClient(self._config)
        self._loop.run_until_complete(self._client.authenticate())
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client and self._loop:
            self._loop.run_until_complete(self._client.close())
            self._loop.close()

    @property
    def e7(self) -> LegacyE7Facade:
        if self._client is None:
            raise RuntimeError("SyncCMSClient is not connected")
        return self._client.e7

    @property
    def rest(self) -> RESTOperations:
        if self._client is None:
            raise RuntimeError("SyncCMSClient is not connected")
        return self._client.rest

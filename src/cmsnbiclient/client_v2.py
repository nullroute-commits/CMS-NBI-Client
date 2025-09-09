import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp
import structlog

from .core.base import BaseClient
from .core.config import Config
from .core.transport import AsyncHTTPTransport
from .REST import RESTOperations
from .security.credentials import SecureCredentialManager

logger = structlog.get_logger()


class CMSClient(BaseClient):
    """Modern async CMS client with all features"""

    def __init__(self, config: Config):
        super().__init__(config)
        self._transport = AsyncHTTPTransport(config)
        self._credential_manager = SecureCredentialManager()
        self._auth_time: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()

        # Operation handlers
        # Note: E7 operations currently require LegacyClient interface
        # self.e7 = E7Operations(self)  # Disabled during transition
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
            response = await self._transport.request(
                method="POST",
                url=url,
                data=payload,
                headers={"Content-Type": "text/xml;charset=ISO-8859-1"},
            )

            # Parse response
            result = await self._parse_auth_response(response)
            self._session_id = result["session_id"]
            self._auth_time = datetime.now()

            self.logger.info("Authentication successful", session_id=self._session_id)

    async def close(self) -> None:
        """Close client and cleanup"""
        if self._session_id:
            try:
                await self._logout()
            except Exception as e:
                self.logger.error(f"Logout failed: {e}")

        await self._transport.close()

    async def _logout(self) -> None:
        """Logout from CMS"""
        payload = self._build_logout_payload()
        url = self._build_netconf_url()

        await self._transport.request(
            method="POST",
            url=url,
            data=payload,
            headers={"Content-Type": "text/xml;charset=ISO-8859-1"},
        )

        self._session_id = None
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

    async def _parse_auth_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse authentication response"""
        text = await response.text()
        # Simple parsing for now - should use proper XML parser
        if "<SessionId>" in text and "</SessionId>" in text:
            start = text.find("<SessionId>") + len("<SessionId>")
            end = text.find("</SessionId>")
            session_id = text[start:end]
            return {"session_id": session_id}
        else:
            raise Exception("Authentication failed - no session ID in response")

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

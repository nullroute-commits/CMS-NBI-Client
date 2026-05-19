"""Regression tests for the modern client implementation."""

from typing import Any, Dict, Optional

import pytest
from pydantic import SecretStr

from cmsnbiclient import CMSClient, Config
from cmsnbiclient.core.config import ConnectionConfig, CredentialsConfig
from cmsnbiclient.core.transport import AsyncHTTPTransport
from cmsnbiclient.exceptions import AuthenticationError
from cmsnbiclient.security.xml import SecureXMLHandler, parse_xml_safely


class FakeResponse:
    """Minimal response stub for auth parsing tests."""

    def __init__(self, body: str):
        self._body = body
        self.released = False

    async def text(self) -> str:
        return self._body

    async def read(self) -> bytes:
        return self._body.encode()

    def release(self) -> None:
        self.released = True


class FakeSessionResponse:
    """Minimal response stub for transport tests."""

    def __init__(self) -> None:
        self.raise_for_status_called = False

    def raise_for_status(self) -> None:
        self.raise_for_status_called = True


class FakeSession:
    """Minimal aiohttp session stub."""

    def __init__(self, response: FakeSessionResponse) -> None:
        self.response = response
        self.request_args: Optional[Dict[str, Any]] = None

    async def request(self, **kwargs: Any) -> FakeSessionResponse:
        self.request_args = kwargs
        return self.response


class FakeTransport:
    """Minimal transport stub for CMSClient authentication."""

    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[Dict[str, Any]] = []

    async def request(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        return self.response

    async def close(self) -> None:
        return None


def make_config(**connection_overrides: Any) -> Config:
    """Create a test config with optional connection overrides."""
    connection = {"protocol": "http", "host": "cms.example.com", "verify_ssl": False}
    connection.update(connection_overrides)
    return Config(
        credentials=CredentialsConfig(username="test-user", password=SecretStr("test-pass")),
        connection=ConnectionConfig.model_validate(connection),
    )


@pytest.mark.asyncio
async def test_transport_returns_live_response_without_context_manager() -> None:
    """Transport should return the response object directly."""
    transport = AsyncHTTPTransport(make_config())
    response = FakeSessionResponse()
    session = FakeSession(response)
    transport._session = session  # type: ignore[assignment]

    result = await transport._do_request("POST", "http://cms.example.com/test")

    assert result is response
    assert response.raise_for_status_called is True
    assert session.request_args is not None
    assert session.request_args["method"] == "POST"


@pytest.mark.asyncio
async def test_authenticate_parses_xml_response_and_updates_session_state() -> None:
    """Authentication should parse XML safely and update legacy compatibility fields."""
    client = CMSClient(make_config(host="127.0.0.1", netconf_port=18080))
    response = FakeResponse(
        """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <auth-reply>
                    <ResultCode>0</ResultCode>
                    <SessionId>12345</SessionId>
                </auth-reply>
            </soapenv:Body>
        </soapenv:Envelope>"""
    )
    client._transport = FakeTransport(response)  # type: ignore[assignment]

    await client.authenticate()

    assert client.session_id == "12345"
    assert response.released is True


@pytest.mark.asyncio
async def test_authenticate_raises_on_invalid_xml() -> None:
    """Authentication should raise a typed error for malformed XML."""
    client = CMSClient(make_config())
    response = FakeResponse("<not-xml")

    with pytest.raises(AuthenticationError):
        await client._parse_auth_response(response)  # type: ignore[arg-type]


def test_rest_query_uses_modern_client_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """REST queries should default to CMSClient configuration instead of legacy literals."""
    client = CMSClient(make_config(host="cms.internal", rest_port=8443))

    captured: Dict[str, Any] = {}

    class Response:
        status_code = 200

        @staticmethod
        def json() -> Dict[str, Any]:
            return {"devices": [{"id": "1"}]}

    def fake_get(**kwargs: Any) -> Response:
        captured.update(kwargs)
        return Response()

    monkeypatch.setattr("cmsnbiclient.REST.query.requests.get", fake_get)

    result = client.rest.query.device(device_type="e7", http_timeout=5)

    assert result == [{"id": "1"}]
    assert captured["url"] == "http://cms.internal:8443/restnbi/devices?deviceType=e7&limit=9999"
    assert captured["auth"] == ("test-user", "test-pass")
    assert captured["timeout"] == 5


def test_secure_xml_helpers_are_available() -> None:
    """Secure XML helpers should parse and build simple XML payloads."""
    parsed = parse_xml_safely("<test><value>ok</value></test>")
    built = SecureXMLHandler().build({"root": {"child": "value"}})

    assert parsed == {"value": "ok"}
    assert built == "<root><child>value</child></root>"

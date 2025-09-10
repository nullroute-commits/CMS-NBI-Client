import asyncio
from typing import Any, Dict, List

import pytest
from aiohttp import web

from cmsnbiclient import CMSClient, Config


class MockCMSServer:
    """Mock CMS server for testing"""

    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.requests: List[Dict[str, Any]] = []

    def setup_routes(self):
        """Setup mock routes"""
        self.app.router.add_post("/cmsexc/ex/netconf", self.handle_netconf)
        self.app.router.add_get("/restnbi/devices", self.handle_devices)

    async def handle_netconf(self, request: web.Request) -> web.Response:
        """Handle NETCONF requests"""
        body = await request.text()
        self.requests.append(
            {"method": "POST", "path": request.path, "body": body, "headers": dict(request.headers)}
        )

        # Parse request and return appropriate response
        if "<login>" in body:
            return web.Response(text=self._build_auth_response("12345"), content_type="text/xml")
        elif "<logout>" in body:
            return web.Response(text=self._build_logout_response(), content_type="text/xml")
        else:
            # Handle other operations
            return web.Response(text=self._build_operation_response(body), content_type="text/xml")

    def _build_auth_response(self, session_id: str) -> str:
        """Build authentication response"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <auth-reply>
                    <ResultCode>0</ResultCode>
                    <SessionId>{session_id}</SessionId>
                </auth-reply>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def _build_logout_response(self) -> str:
        """Build logout response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <logout-reply>
                    <ResultCode>0</ResultCode>
                </logout-reply>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def _build_operation_response(self, request_body: str) -> str:
        """Build operation response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <rpc-reply>
                    <ok/>
                </rpc-reply>
            </soapenv:Body>
        </soapenv:Envelope>"""

    async def handle_devices(self, request: web.Request) -> web.Response:
        """Handle REST device requests"""
        return web.json_response(
            {
                "devices": [
                    {"id": "1", "name": "Device1", "type": "E7"},
                    {"id": "2", "name": "Device2", "type": "E7"},
                ]
            }
        )


@pytest.fixture
async def mock_server(aiohttp_server):
    """Create mock CMS server"""
    server = MockCMSServer()
    app_server = await aiohttp_server(server.app)
    server.url = str(app_server.make_url("/"))
    server.host = app_server.host
    server.port = app_server.port
    return server


@pytest.fixture
async def client(mock_server):
    """Create test client"""
    config = Config(
        connection={
            "protocol": "http",
            "host": mock_server.host,
            "netconf_port": mock_server.port,
            "verify_ssl": False,
        },
        credentials={"username": "test_user", "password": "test_pass"},
    )

    async with CMSClient(config) as client:
        yield client


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

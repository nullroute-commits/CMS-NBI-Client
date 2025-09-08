#!/usr/bin/env python3
"""Mock CMS server for testing"""

import os
import json
from aiohttp import web
import structlog

logger = structlog.get_logger()

class MockCMSServer:
    """Mock CMS server for testing"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.sessions = {}
        self.requests_log = []
        
    def setup_routes(self):
        """Setup mock routes"""
        # NETCONF routes
        self.app.router.add_post('/cmsexc/ex/netconf', self.handle_netconf)
        
        # REST routes
        self.app.router.add_get('/restnbi/devices', self.handle_devices)
        self.app.router.add_get('/restnbi/devices/{device_id}', self.handle_device_info)
        
        # Health check
        self.app.router.add_get('/health', self.handle_health)
        
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "mock-cms"})
        
    async def handle_netconf(self, request: web.Request) -> web.Response:
        """Handle NETCONF requests"""
        body = await request.text()
        self.requests_log.append({
            'method': 'POST',
            'path': request.path,
            'body': body,
            'headers': dict(request.headers)
        })
        
        # Parse request and return appropriate response
        if '<auth-req>' in body:
            return web.Response(
                text=self._build_auth_response('mock-session-12345'),
                content_type='text/xml'
            )
        elif '<logout-req>' in body:
            return web.Response(
                text=self._build_logout_response(),
                content_type='text/xml'
            )
        elif '<rpc' in body:
            return web.Response(
                text=self._build_rpc_response(body),
                content_type='text/xml'
            )
        else:
            return web.Response(
                text=self._build_error_response("Unknown request"),
                content_type='text/xml',
                status=400
            )
    
    def _build_auth_response(self, session_id: str) -> str:
        """Build authentication response"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <auth-reply>
            <ResultCode>0</ResultCode>
            <SessionId>{session_id}</SessionId>
            <MaxSessionTimeout>3600</MaxSessionTimeout>
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
            <ResultString>Success</ResultString>
        </logout-reply>
    </soapenv:Body>
</soapenv:Envelope>"""

    def _build_rpc_response(self, request_body: str) -> str:
        """Build RPC response based on request"""
        if 'query-ont' in request_body:
            return self._build_ont_query_response()
        elif 'create-ont' in request_body:
            return self._build_create_response()
        else:
            return self._build_generic_ok_response()
    
    def _build_ont_query_response(self) -> str:
        """Build ONT query response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <rpc-reply>
            <data>
                <ont>
                    <ont-id>12345</ont-id>
                    <admin-state>enabled</admin-state>
                    <serial-number>CXNK12345678</serial-number>
                    <description>Test ONT</description>
                </ont>
            </data>
        </rpc-reply>
    </soapenv:Body>
</soapenv:Envelope>"""
    
    def _build_create_response(self) -> str:
        """Build create response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <rpc-reply>
            <ok/>
        </rpc-reply>
    </soapenv:Body>
</soapenv:Envelope>"""
    
    def _build_generic_ok_response(self) -> str:
        """Build generic OK response"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <rpc-reply>
            <ok/>
        </rpc-reply>
    </soapenv:Body>
</soapenv:Envelope>"""
    
    def _build_error_response(self, error_msg: str) -> str:
        """Build error response"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <rpc-reply>
            <rpc-error>
                <error-message>{error_msg}</error-message>
            </rpc-error>
        </rpc-reply>
    </soapenv:Body>
</soapenv:Envelope>"""
    
    async def handle_devices(self, request: web.Request) -> web.Response:
        """Handle REST device list request"""
        devices = [
            {"id": "1", "name": "E7-Device-1", "type": "E7", "status": "online"},
            {"id": "2", "name": "E7-Device-2", "type": "E7", "status": "online"},
            {"id": "3", "name": "E7-Device-3", "type": "E7", "status": "offline"}
        ]
        return web.json_response({"devices": devices})
    
    async def handle_device_info(self, request: web.Request) -> web.Response:
        """Handle REST device info request"""
        device_id = request.match_info['device_id']
        device = {
            "id": device_id,
            "name": f"E7-Device-{device_id}",
            "type": "E7",
            "status": "online",
            "version": "2.5.1",
            "uptime": "30 days"
        }
        return web.json_response(device)


def main():
    """Run mock server"""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ]
    )
    
    # Create and run server
    server = MockCMSServer()
    port = int(os.getenv('MOCK_SERVER_PORT', 18443))
    
    logger.info(f"Starting mock CMS server on port {port}")
    web.run_app(server.app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
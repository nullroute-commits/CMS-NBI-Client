# REST SUBPACKAGES IMPORT STATEMENTS
from .query import Query


class RESTOperations:
    """REST operations wrapper"""

    def __init__(self, client):
        self.client = client
        self.query = Query(client)

    # Delegate common operations
    async def query_devices(self, **kwargs):
        return await self.query.devices(**kwargs)


__all__ = ["RESTOperations", "Query"]

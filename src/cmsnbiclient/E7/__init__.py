# E7 SUBPACKAGES IMPORT STATEMENTS
from .create import Create
from .delete import Delete
from .query import Query
from .update import Update


class E7Operations:
    """E7 operations wrapper"""

    def __init__(self, client):
        self.client = client
        self.create = Create(client)
        self.delete = Delete(client)
        self.query = Query(client)
        self.update = Update(client)

    # Delegate common operations
    async def create_ont(self, **kwargs):
        return await self.create.ont(**kwargs)

    async def delete_ont(self, **kwargs):
        return await self.delete.ont(**kwargs)

    async def query_ont(self, **kwargs):
        return await self.query.ont(**kwargs)

    async def update_ont(self, **kwargs):
        return await self.update.ont(**kwargs)


__all__ = ["E7Operations", "Create", "Delete", "Query", "Update"]

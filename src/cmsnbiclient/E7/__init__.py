# E7 SUBPACKAGES IMPORT STATEMENTS
from typing import Any

from .create import Create
from .delete import Delete
from .query import Query
from .update import Update


class E7Operations:
    """E7 operations wrapper"""

    def __init__(self, client: Any) -> None:
        self.client = client
        self.create = Create(client)
        self.delete = Delete(client)
        self.query = Query(client)
        self.update = Update(client)

    # Delegate common operations
    def create_ont(self, **kwargs: Any) -> Any:
        return self.create.ont(**kwargs)

    def delete_ont(self, **kwargs: Any) -> Any:
        return self.delete.ont(**kwargs)

    def update_ont(self, **kwargs: Any) -> Any:
        return self.update.ont(**kwargs)


__all__ = ["E7Operations", "Create", "Delete", "Query", "Update"]

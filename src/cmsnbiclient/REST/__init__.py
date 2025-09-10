# REST SUBPACKAGES IMPORT STATEMENTS
from typing import Any

from .query import Query


class RESTOperations:
    """REST operations wrapper"""

    def __init__(self, client: Any) -> None:
        self.client = client
        self.query = Query(client)

    # Delegate common operations
    def query_devices(self, **kwargs: Any) -> Any:
        return self.query.device(**kwargs)


__all__ = ["RESTOperations", "Query"]

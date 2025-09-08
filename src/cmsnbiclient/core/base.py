from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, TypeVar, Union
import asyncio
from contextlib import asynccontextmanager
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

T = TypeVar('T')


class TransportProtocol(Protocol):
    """Protocol for transport implementations"""
    
    async def request(
        self, 
        method: str, 
        url: str, 
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> 'Response':
        ...


class BaseClient(ABC):
    """Abstract base class for CMS clients"""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.logger = logger.bind(client=self.__class__.__name__)
        self._session_id: Optional[str] = None
        self._transport: Optional[TransportProtocol] = None
    
    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with CMS"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close client connections"""
        pass
    
    async def __aenter__(self):
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class BaseOperation(ABC):
    """Abstract base class for CRUD operations"""
    
    def __init__(self, client: BaseClient, network_name: str):
        self.client = client
        self.network_name = network_name
        self.logger = logger.bind(
            operation=self.__class__.__name__,
            network=network_name
        )
    
    @property
    @abstractmethod
    def operation_type(self) -> str:
        """Return operation type (create, read, update, delete)"""
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def execute(self, **kwargs) -> Any:
        """Execute operation with retry logic"""
        self.logger.info(f"Executing {self.operation_type} operation", **kwargs)
        try:
            return await self._execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Operation failed: {e}", exc_info=True)
            raise
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """Implementation of operation execution"""
        pass
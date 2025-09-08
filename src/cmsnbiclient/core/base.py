"""Base classes and protocols for CMS-NBI-Client.

This module provides the abstract base classes and protocols that define
the core interfaces for the CMS-NBI-Client library. All concrete implementations
inherit from these base classes.

Classes:
    TransportProtocol: Protocol defining transport layer interface
    BaseClient: Abstract base class for CMS client implementations
    BaseOperation: Abstract base class for CRUD operations

Example:
    ```python
    from cmsnbiclient.core.base import BaseClient, BaseOperation
    
    class MyCustomClient(BaseClient):
        async def authenticate(self) -> None:
            # Custom authentication logic
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, TypeVar, Union
import asyncio
from contextlib import asynccontextmanager
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

T = TypeVar('T')


class TransportProtocol(Protocol):
    """Protocol defining the transport layer interface.
    
    This protocol defines the contract that all transport implementations
    must follow. It ensures consistent behavior across different transport
    mechanisms (HTTP, HTTPS, etc.).
    
    Methods:
        request: Execute a network request and return response
    """
    
    async def request(
        self, 
        method: str, 
        url: str, 
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> 'Response':
        """Execute a network request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to send request to
            data: Optional request body data
            headers: Optional HTTP headers
            timeout: Optional request timeout in seconds
            
        Returns:
            Response object from the transport layer
            
        Raises:
            TransportError: If the request fails
        """
        ...


class BaseClient(ABC):
    """Abstract base class for CMS client implementations.
    
    This class provides the foundation for all CMS client implementations.
    It handles common functionality like configuration management, logging,
    and session lifecycle.
    
    Attributes:
        config: Configuration object containing connection and auth details
        logger: Structured logger instance for this client
        
    Example:
        ```python
        class MyClient(BaseClient):
            async def authenticate(self) -> None:
                # Implement authentication
                self._session_id = await self._login()
                
            async def close(self) -> None:
                # Cleanup resources
                await self._logout()
        ```
    """
    
    def __init__(self, config: 'Config'):
        """Initialize the base client.
        
        Args:
            config: Configuration object with connection and credential details
        """
        self.config = config
        self.logger = logger.bind(client=self.__class__.__name__)
        self._session_id: Optional[str] = None
        self._transport: Optional[TransportProtocol] = None
    
    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the CMS system.
        
        This method must be implemented by subclasses to handle
        authentication specific to the CMS API being used.
        
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close client connections and cleanup resources.
        
        This method must be implemented by subclasses to properly
        close connections and cleanup any resources.
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry.
        
        Authenticates the client when entering the context.
        
        Returns:
            Self for use in async with statements
        """
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.
        
        Closes the client when exiting the context.
        """
        await self.close()


class BaseOperation(ABC):
    """Abstract base class for CRUD operations.
    
    This class provides a template for all CRUD operations in the system.
    It includes built-in retry logic, logging, and error handling.
    
    Attributes:
        client: Reference to the parent client instance
        network_name: Name of the network to operate on
        logger: Structured logger with operation context
        
    Example:
        ```python
        class CreateONTOperation(BaseOperation):
            @property
            def operation_type(self) -> str:
                return "create"
                
            async def _execute(self, ont_id: str, **kwargs) -> Dict[str, Any]:
                # Implementation of ONT creation
                return await self.client.create_resource("ont", ont_id, kwargs)
        ```
    """
    
    def __init__(self, client: BaseClient, network_name: str):
        """Initialize the operation.
        
        Args:
            client: Parent client instance
            network_name: Network name to operate on
        """
        self.client = client
        self.network_name = network_name
        self.logger = logger.bind(
            operation=self.__class__.__name__,
            network=network_name
        )
    
    @property
    @abstractmethod
    def operation_type(self) -> str:
        """Return the operation type.
        
        Must return one of: 'create', 'read', 'update', 'delete'
        
        Returns:
            String identifying the operation type
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def execute(self, **kwargs) -> Any:
        """Execute the operation with retry logic.
        
        This method wraps the actual operation execution with:
        - Automatic retry on failure (3 attempts)
        - Exponential backoff between retries
        - Structured logging of execution
        - Error handling and reporting
        
        Args:
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result (type depends on operation)
            
        Raises:
            OperationError: If operation fails after all retries
        """
        self.logger.info(f"Executing {self.operation_type} operation", **kwargs)
        try:
            return await self._execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Operation failed: {e}", exc_info=True)
            raise
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """Implementation of the actual operation execution.
        
        This method must be implemented by subclasses to perform
        the actual operation logic.
        
        Args:
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result
            
        Raises:
            OperationError: If operation fails
        """
        pass
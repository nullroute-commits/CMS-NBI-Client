"""Exception classes for CMS NBI Client."""


class CMSClientError(Exception):
    """Base exception for all CMS client errors."""
    pass


class AuthenticationError(CMSClientError):
    """Raised when authentication fails."""
    pass


class ConnectionError(CMSClientError):
    """Raised when connection to CMS fails."""
    pass


class OperationError(CMSClientError):
    """Raised when an operation fails."""
    pass


class ValidationError(CMSClientError):
    """Raised when input validation fails."""
    pass


class TimeoutError(CMSClientError):
    """Raised when operations timeout."""
    pass


class NetworkError(CMSClientError):
    """Raised when network operations fail."""
    pass
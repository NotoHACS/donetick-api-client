"""Custom exceptions for Donetick API client."""


class DonetickError(Exception):
    """Base exception for all Donetick API errors."""
    pass


class DonetickAuthError(DonetickError):
    """Raised when authentication fails (401)."""
    pass


class DonetickNotFoundError(DonetickError):
    """Raised when a resource is not found (404)."""
    pass


class DonetickValidationError(DonetickError):
    """Raised when request validation fails (400)."""
    pass


class DonetickRateLimitError(DonetickError):
    """Raised when rate limit is exceeded (429)."""
    pass

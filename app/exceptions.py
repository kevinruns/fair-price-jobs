"""
Custom exception classes for the Jobeco application.
"""

class JobecoException(Exception):
    """Base exception class for Jobeco application."""

    def __init__(self, message: str, error_code: str = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class ValidationError(JobecoException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code, 400)
        self.field = field

class AuthenticationError(JobecoException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, error_code, 401)

class AuthorizationError(JobecoException):
    """Raised when user doesn't have permission to perform an action."""

    def __init__(self, message: str = "Insufficient permissions", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, error_code, 403)

class NotFoundError(JobecoException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND_ERROR"):
        super().__init__(message, error_code, 404)

class DatabaseError(JobecoException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database operation failed", error_code: str = "DATABASE_ERROR"):
        super().__init__(message, error_code, 500)

class DuplicateResourceError(JobecoException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, message: str = "Resource already exists", error_code: str = "DUPLICATE_RESOURCE_ERROR"):
        super().__init__(message, error_code, 409)

class RateLimitError(JobecoException):
    """Raised when rate limiting is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT_ERROR"):
        super().__init__(message, error_code, 429)

class ConfigurationError(JobecoException):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str = "Configuration error", error_code: str = "CONFIGURATION_ERROR"):
        super().__init__(message, error_code, 500)
        
"""Shared AMIII exception types."""


class AMIIIError(Exception):
    """Base exception for AMIII errors."""


class ConfigurationError(AMIIIError):
    """Raised when required configuration is missing or invalid."""


class DependencyMissingError(AMIIIError):
    """Raised when an optional external dependency is required but unavailable."""


class ProviderUnavailableError(AMIIIError):
    """Raised when an LLM provider cannot complete a request."""


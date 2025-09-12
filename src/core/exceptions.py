"""Custom exceptions for DNB Presentation Generator."""

from typing import Optional, Dict, Any


class DNBPresentationError(Exception):
    """Base exception for DNB Presentation Generator."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(DNBPresentationError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(DNBPresentationError):
    """Raised when authorization fails."""
    pass


class ValidationError(DNBPresentationError):
    """Raised when data validation fails."""
    pass


class DocumentProcessingError(DNBPresentationError):
    """Raised when document processing fails."""
    pass


class LLMServiceError(DNBPresentationError):
    """Raised when LLM service encounters an error."""
    pass


class PresentationGenerationError(DNBPresentationError):
    """Raised when presentation generation fails."""
    pass


class ComplianceError(DNBPresentationError):
    """Raised when compliance checks fail."""
    pass


class PIIDetectionError(DNBPresentationError):
    """Raised when PII detection fails."""
    pass


class ContentSafetyError(DNBPresentationError):
    """Raised when content safety checks fail."""
    pass


class ExportError(DNBPresentationError):
    """Raised when export operations fail."""
    pass


class ConfigurationError(DNBPresentationError):
    """Raised when configuration is invalid."""
    pass


class ExternalServiceError(DNBPresentationError):
    """Raised when external service calls fail."""
    pass


class RateLimitError(DNBPresentationError):
    """Raised when rate limits are exceeded."""
    pass


class StorageError(DNBPresentationError):
    """Raised when storage operations fail."""
    pass


class CacheError(DNBPresentationError):
    """Raised when cache operations fail."""
    pass


class AgentError(DNBPresentationError):
    """Raised when agent execution fails."""
    pass


class WorkflowError(DNBPresentationError):
    """Raised when workflow execution fails."""
    pass


class TemplateError(DNBPresentationError):
    """Raised when template operations fail."""
    pass


class AssetError(DNBPresentationError):
    """Raised when asset operations fail."""
    pass


class ChartGenerationError(DNBPresentationError):
    """Raised when chart generation fails."""
    pass


class AccessibilityError(DNBPresentationError):
    """Raised when accessibility checks fail."""
    pass


class BrandComplianceError(DNBPresentationError):
    """Raised when brand compliance checks fail."""
    pass


class BackupError(DNBPresentationError):
    """Raised when backup operations fail."""
    pass


class MonitoringError(DNBPresentationError):
    """Raised when monitoring operations fail."""
    pass


# HTTP Status Code Mapping
EXCEPTION_STATUS_CODES = {
    AuthenticationError: 401,
    AuthorizationError: 403,
    ValidationError: 400,
    DocumentProcessingError: 422,
    LLMServiceError: 502,
    PresentationGenerationError: 500,
    ComplianceError: 422,
    PIIDetectionError: 422,
    ContentSafetyError: 422,
    ExportError: 500,
    ConfigurationError: 500,
    ExternalServiceError: 502,
    RateLimitError: 429,
    StorageError: 500,
    CacheError: 500,
    AgentError: 500,
    WorkflowError: 500,
    TemplateError: 422,
    AssetError: 404,
    ChartGenerationError: 500,
    AccessibilityError: 422,
    BrandComplianceError: 422,
    BackupError: 500,
    MonitoringError: 500,
}

"""Application constants for DNB Presentation Generator."""

from enum import Enum
from typing import Dict, List


class SlideType(str, Enum):
    """Slide type enumeration."""
    TITLE = "title"
    CONTENT = "content"
    BULLET_POINTS = "bullet_points"
    IMAGE = "image"
    CHART = "chart"
    QUOTE = "quote"
    COMPARISON = "comparison"
    CONCLUSION = "conclusion"
    SECTION_BREAK = "section_break"


class ChartType(str, Enum):
    """Chart type enumeration."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    COLUMN = "column"
    DONUT = "donut"
    WATERFALL = "waterfall"
    COMBO = "combo"


class PresentationTemplate(str, Enum):
    """Presentation template enumeration."""
    CORPORATE = "corporate"
    EXECUTIVE = "executive"
    RESEARCH = "research"
    MARKETING = "marketing"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    QUARTERLY = "quarterly"


class DocumentType(str, Enum):
    """Document type enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


class ExportFormat(str, Enum):
    """Export format enumeration."""
    PPTX = "pptx"
    PDF = "pdf"
    GOOGLE_SLIDES = "google_slides"
    JSON = "json"


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuditAction(str, Enum):
    """Audit action enumeration."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    GENERATE = "generate"
    APPROVE = "approve"
    REJECT = "reject"


class PIICategory(str, Enum):
    """PII category enumeration."""
    PERSON = "person"
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IBAN = "iban"
    IP_ADDRESS = "ip_address"
    LOCATION = "location"
    DATE_OF_BIRTH = "date_of_birth"


class ComplianceLevel(str, Enum):
    """Compliance level enumeration."""
    STRICT = "strict"
    MODERATE = "moderate"
    RELAXED = "relaxed"


class ContentSafetyLevel(str, Enum):
    """Content safety level enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentType(str, Enum):
    """Agent type enumeration."""
    PLANNER = "planner"
    RESEARCH = "research"
    CONTENT = "content"
    ARCHITECT = "architect"
    QA_COMPLIANCE = "qa_compliance"
    EXPORT = "export"


class WorkflowState(str, Enum):
    """Workflow state enumeration."""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    RESEARCHING = "researching"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    ERROR = "error"


# File size limits
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_SLIDES_PER_PRESENTATION = 25
MAX_BULLET_POINTS_PER_SLIDE = 7
MAX_CHART_DATA_POINTS = 50

# Supported file types
SUPPORTED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".html": "text/html",
}

# DNB Brand Colors
DNB_BRAND_COLORS = {
    "primary": "#00524C",
    "secondary": "#FF6B35",
    "accent": "#FFE66D",
    "neutral_dark": "#2C2C2C",
    "neutral_light": "#F5F5F5",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
}

# Accessibility Guidelines
WCAG_CONTRAST_RATIOS = {
    "AA_NORMAL": 4.5,
    "AA_LARGE": 3.0,
    "AAA_NORMAL": 7.0,
    "AAA_LARGE": 4.5,
}

# Font Specifications
DNB_FONTS = {
    "primary": "DNB Sans",
    "secondary": "Arial",
    "fallback": "sans-serif",
    "minimum_size": 12,
    "heading_size": 24,
    "body_size": 14,
}

# Chart Specifications
CHART_DEFAULTS = {
    "width": 800,
    "height": 600,
    "dpi": 300,
    "font_family": "DNB Sans",
    "color_palette": list(DNB_BRAND_COLORS.values()),
}

# API Configuration
API_CONFIG = {
    "version": "v1",
    "prefix": "/api/v1",
    "title": "DNB Presentation Generator API",
    "description": "Enterprise presentation generation service",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
}

# Rate Limiting
RATE_LIMITS = {
    "default": "100/minute",
    "generation": "10/minute",
    "upload": "20/minute",
    "export": "30/minute",
}

# Cache TTL (seconds)
CACHE_TTL = {
    "short": 300,      # 5 minutes
    "medium": 3600,    # 1 hour
    "long": 86400,     # 24 hours
    "assets": 604800,  # 1 week
}

# Monitoring and Metrics
METRICS_CONFIG = {
    "histogram_buckets": [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0],
    "collection_interval": 15,  # seconds
    "retention_days": 90,
}

# Backup Configuration
BACKUP_CONFIG = {
    "retention_days": 30,
    "compression": True,
    "encryption": True,
    "verify_integrity": True,
}

# Content Safety Thresholds
CONTENT_SAFETY_THRESHOLDS = {
    "hate": 0.7,
    "self_harm": 0.7,
    "sexual": 0.7,
    "violence": 0.7,
}

# PII Detection Patterns
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b\d{3}-?\d{3}-?\d{4}\b",
    "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
}

# Error Messages
ERROR_MESSAGES = {
    "file_too_large": "File size exceeds maximum allowed size of {max_size}MB",
    "unsupported_file_type": "File type not supported. Allowed types: {types}",
    "pii_detected": "Personal information detected and redacted",
    "content_safety_violation": "Content violates safety guidelines",
    "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
    "insufficient_permissions": "Insufficient permissions to perform this action",
    "generation_failed": "Presentation generation failed: {reason}",
    "export_failed": "Export operation failed: {reason}",
}

# Success Messages
SUCCESS_MESSAGES = {
    "file_uploaded": "File uploaded successfully",
    "presentation_generated": "Presentation generated successfully",
    "presentation_exported": "Presentation exported successfully",
    "user_authenticated": "User authenticated successfully",
    "settings_updated": "Settings updated successfully",
}

# Template Metadata
TEMPLATE_METADATA = {
    "corporate": {
        "name": "Corporate Template",
        "description": "Professional corporate presentation template",
        "max_slides": 25,
        "supports_charts": True,
        "supports_images": True,
    },
    "executive": {
        "name": "Executive Summary Template",
        "description": "Executive-level presentation template",
        "max_slides": 15,
        "supports_charts": True,
        "supports_images": False,
    },
    "research": {
        "name": "Research Template",
        "description": "Data-driven research presentation template",
        "max_slides": 30,
        "supports_charts": True,
        "supports_images": True,
    },
}

# Agent Configuration
AGENT_CONFIG = {
    "max_iterations": 10,
    "timeout_seconds": 300,
    "retry_attempts": 3,
    "parallel_execution": True,
}

# Workflow Configuration
WORKFLOW_CONFIG = {
    "max_execution_time": 600,  # 10 minutes
    "checkpoint_interval": 30,  # seconds
    "state_persistence": True,
    "error_recovery": True,
}

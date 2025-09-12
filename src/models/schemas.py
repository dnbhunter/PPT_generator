"""Pydantic schemas for DNB Presentation Generator."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..core.constants import (
    SlideType, ChartType, PresentationTemplate, DocumentType,
    ExportFormat, UserRole, JobStatus, AuditAction, AgentType,
    WorkflowState, PIICategory
)


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )


# User and Authentication Schemas
class UserBase(BaseSchema):
    """Base user schema."""
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    is_active: bool = Field(default=True, description="User active status")


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseSchema):
    """User update schema."""
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """User response schema."""
    id: UUID = Field(default_factory=uuid4, description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")


class TokenData(BaseSchema):
    """Token data schema."""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


# Document Schemas
class DocumentMetadata(BaseSchema):
    """Document metadata schema."""
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    document_type: DocumentType = Field(..., description="Document type")
    language: Optional[str] = Field(default="en", description="Document language")
    encoding: Optional[str] = Field(default="utf-8", description="Document encoding")


class DocumentUpload(BaseSchema):
    """Document upload schema."""
    content: str = Field(..., description="Document content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    extract_images: bool = Field(default=False, description="Extract images from document")
    detect_pii: bool = Field(default=True, description="Detect PII in document")


class ProcessedDocument(BaseSchema):
    """Processed document schema."""
    id: UUID = Field(default_factory=uuid4, description="Document ID")
    content: str = Field(..., description="Processed content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    pii_detected: List[PIICategory] = Field(default=[], description="Detected PII categories")
    extracted_data: Dict[str, Any] = Field(default={}, description="Extracted structured data")
    processing_stats: Dict[str, Any] = Field(default={}, description="Processing statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


# Slide Schemas
class SlideContent(BaseSchema):
    """Slide content schema."""
    title: str = Field(..., description="Slide title")
    content: List[str] = Field(default=[], description="Slide content items")
    speaker_notes: Optional[str] = Field(default=None, description="Speaker notes")
    image_url: Optional[str] = Field(default=None, description="Image URL")
    chart_data: Optional[Dict[str, Any]] = Field(default=None, description="Chart data")


class SlideCreate(BaseSchema):
    """Slide creation schema."""
    slide_type: SlideType = Field(..., description="Slide type")
    content: SlideContent = Field(..., description="Slide content")
    order: int = Field(..., description="Slide order in presentation")
    template_overrides: Dict[str, Any] = Field(default={}, description="Template overrides")


class Slide(SlideCreate):
    """Slide response schema."""
    id: UUID = Field(default_factory=uuid4, description="Slide ID")
    presentation_id: UUID = Field(..., description="Parent presentation ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")


# Chart Schemas
class ChartData(BaseSchema):
    """Chart data schema."""
    labels: List[str] = Field(..., description="Chart labels")
    datasets: List[Dict[str, Any]] = Field(..., description="Chart datasets")
    chart_type: ChartType = Field(..., description="Chart type")
    title: str = Field(..., description="Chart title")
    options: Dict[str, Any] = Field(default={}, description="Chart options")


class ChartGeneration(BaseSchema):
    """Chart generation request schema."""
    data: ChartData = Field(..., description="Chart data")
    style: Dict[str, Any] = Field(default={}, description="Chart styling")
    accessibility: Dict[str, Any] = Field(default={}, description="Accessibility options")


# Presentation Schemas
class PresentationMetadata(BaseSchema):
    """Presentation metadata schema."""
    title: str = Field(..., description="Presentation title")
    description: Optional[str] = Field(default=None, description="Presentation description")
    template: PresentationTemplate = Field(default=PresentationTemplate.CORPORATE, description="Template")
    author: str = Field(..., description="Presentation author")
    company: str = Field(default="DNB Bank ASA", description="Company name")
    tags: List[str] = Field(default=[], description="Presentation tags")


class PresentationCreate(BaseSchema):
    """Presentation creation schema."""
    metadata: PresentationMetadata = Field(..., description="Presentation metadata")
    source_document_id: Optional[UUID] = Field(default=None, description="Source document ID")
    generation_options: Dict[str, Any] = Field(default={}, description="Generation options")


class PresentationUpdate(BaseSchema):
    """Presentation update schema."""
    metadata: Optional[PresentationMetadata] = None
    generation_options: Optional[Dict[str, Any]] = None


class Presentation(PresentationCreate):
    """Presentation response schema."""
    id: UUID = Field(default_factory=uuid4, description="Presentation ID")
    user_id: UUID = Field(..., description="Owner user ID")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Generation status")
    slides: List[Slide] = Field(default=[], description="Presentation slides")
    generation_stats: Dict[str, Any] = Field(default={}, description="Generation statistics")
    export_urls: Dict[ExportFormat, str] = Field(default={}, description="Export URLs")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")


# Job and Workflow Schemas
class JobCreate(BaseSchema):
    """Job creation schema."""
    job_type: str = Field(..., description="Job type")
    payload: Dict[str, Any] = Field(..., description="Job payload")
    priority: int = Field(default=5, description="Job priority (1-10)")
    scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled execution time")


class Job(JobCreate):
    """Job response schema."""
    id: UUID = Field(default_factory=uuid4, description="Job ID")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Job status")
    user_id: UUID = Field(..., description="User ID")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Job result")
    error_message: Optional[str] = Field(default=None, description="Error message")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


# Agent and Workflow Schemas
class AgentState(BaseSchema):
    """Agent state schema."""
    workflow_id: UUID = Field(..., description="Workflow ID")
    current_agent: AgentType = Field(..., description="Current agent type")
    state: WorkflowState = Field(..., description="Workflow state")
    data: Dict[str, Any] = Field(default={}, description="State data")
    history: List[Dict[str, Any]] = Field(default=[], description="State history")
    metadata: Dict[str, Any] = Field(default={}, description="State metadata")


class AgentResult(BaseSchema):
    """Agent execution result schema."""
    success: bool = Field(..., description="Execution success status")
    data: Dict[str, Any] = Field(default={}, description="Result data")
    messages: List[str] = Field(default=[], description="Result messages")
    errors: List[str] = Field(default=[], description="Error messages")
    agent_name: str = Field(..., description="Agent name")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default={}, description="Result metadata")


class WorkflowExecution(BaseSchema):
    """Workflow execution schema."""
    id: UUID = Field(default_factory=uuid4, description="Workflow ID")
    presentation_id: UUID = Field(..., description="Presentation ID")
    user_id: UUID = Field(..., description="User ID")
    state: WorkflowState = Field(default=WorkflowState.INITIALIZED, description="Workflow state")
    agent_results: List[AgentResult] = Field(default=[], description="Agent results")
    total_execution_time: float = Field(default=0.0, description="Total execution time")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")


# Export Schemas
class ExportRequest(BaseSchema):
    """Export request schema."""
    presentation_id: UUID = Field(..., description="Presentation ID")
    format: ExportFormat = Field(..., description="Export format")
    options: Dict[str, Any] = Field(default={}, description="Export options")
    include_speaker_notes: bool = Field(default=True, description="Include speaker notes")
    include_metadata: bool = Field(default=False, description="Include metadata")


class ExportResult(BaseSchema):
    """Export result schema."""
    id: UUID = Field(default_factory=uuid4, description="Export ID")
    presentation_id: UUID = Field(..., description="Presentation ID")
    format: ExportFormat = Field(..., description="Export format")
    file_url: str = Field(..., description="Download URL")
    file_size: int = Field(..., description="File size in bytes")
    expires_at: datetime = Field(..., description="URL expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


# Audit Schemas
class AuditLog(BaseSchema):
    """Audit log schema."""
    id: UUID = Field(default_factory=uuid4, description="Audit log ID")
    user_id: UUID = Field(..., description="User ID")
    action: AuditAction = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[UUID] = Field(default=None, description="Resource ID")
    details: Dict[str, Any] = Field(default={}, description="Action details")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")


# Health Check Schemas
class HealthCheck(BaseSchema):
    """Health check schema."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    services: Dict[str, str] = Field(default={}, description="Service statuses")


# API Response Schemas
class APIResponse(BaseSchema):
    """Generic API response schema."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(default="", description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    errors: List[str] = Field(default=[], description="Error messages")
    metadata: Dict[str, Any] = Field(default={}, description="Response metadata")


class PaginatedResponse(APIResponse):
    """Paginated response schema."""
    total: int = Field(..., description="Total items count")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages count")


# Configuration Schemas
class ComplianceSettings(BaseSchema):
    """Compliance settings schema."""
    pii_detection_enabled: bool = Field(default=True, description="Enable PII detection")
    content_safety_enabled: bool = Field(default=True, description="Enable content safety")
    audit_logging_enabled: bool = Field(default=True, description="Enable audit logging")
    data_retention_days: int = Field(default=2555, description="Data retention period")
    strict_mode: bool = Field(default=True, description="Enable strict compliance mode")


class GenerationSettings(BaseSchema):
    """Generation settings schema."""
    max_slides: int = Field(default=25, description="Maximum slides per presentation")
    enable_charts: bool = Field(default=True, description="Enable chart generation")
    enable_images: bool = Field(default=True, description="Enable image inclusion")
    ai_creativity: float = Field(default=0.3, description="AI creativity level (0-1)")
    language: str = Field(default="en", description="Output language")


class SystemSettings(BaseSchema):
    """System settings schema."""
    compliance: ComplianceSettings = Field(default_factory=ComplianceSettings, description="Compliance settings")
    generation: GenerationSettings = Field(default_factory=GenerationSettings, description="Generation settings")
    feature_flags: Dict[str, bool] = Field(default={}, description="Feature flags")
    updated_by: UUID = Field(..., description="User who updated settings")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")

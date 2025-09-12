"""Core configuration management for DNB Presentation Generator."""

import os
from enum import Enum
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Environment(str, Enum):
    """Application environment enumeration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Configuration
    app_name: str = "DNB Presentation Generator"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: LogLevel = LogLevel.INFO
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    worker_processes: int = 4
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 300
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production-12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    allowed_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    allowed_headers: str = "*"
    
    # Azure Configuration
    azure_tenant_id: str = "mock-tenant-id"
    azure_client_id: str = "mock-client-id"
    azure_client_secret: str = "mock-client-secret"
    azure_subscription_id: str = "mock-subscription-id"
    azure_resource_group: str = "mock-rg"
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = "https://mock-openai.openai.azure.com/"
    azure_openai_api_key: str = "mock-api-key"
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_model_name: str = "gpt-4o"
    
    # Azure Key Vault
    azure_key_vault_url: str = "https://mock-keyvault.vault.azure.net/"
    
    # Database Configuration
    database_url: str = "sqlite:///./presentations.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    cache_ttl_seconds: int = 3600
    
    # File Upload Configuration
    max_file_size: str = "50MB"
    allowed_file_types: str = ".pdf,.docx,.txt,.md"
    upload_directory: str = "./uploads"
    
    # Azure Storage Configuration
    azure_storage_account_name: str = "mockstorageaccount"
    azure_storage_container_name: str = "documents"
    azure_storage_connection_string: str = "DefaultEndpointsProtocol=https;AccountName=mockstorageaccount;AccountKey=mockkey;EndpointSuffix=core.windows.net"
    
    # Presentation Configuration
    max_slides_per_presentation: int = 25
    default_template: str = "corporate"
    chart_generation_enabled: bool = True
    image_search_enabled: bool = True
    
    # Compliance Configuration
    pii_detection_enabled: bool = True
    content_safety_enabled: bool = True
    audit_logging_enabled: bool = True
    data_retention_days: int = 30
    
    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_port: int = 9090
    sentry_dsn: Optional[str] = None
    application_insights_connection_string: Optional[str] = None
    
    # Feature Flags
    enable_experimental_features: bool = False
    enable_advanced_charts: bool = True
    enable_ai_suggestions: bool = True
    enable_collaborative_editing: bool = False
    
    # External Services
    corporate_asset_api_url: Optional[str] = None
    knowledge_base_api_url: Optional[str] = None
    dlp_service_url: Optional[str] = None
    
    # Email Configuration
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10
    
    # Backup Configuration
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    @property
    def upload_path(self) -> Path:
        """Get upload directory as Path object."""
        return Path(self.upload_directory)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @property
    def allowed_methods_list(self) -> List[str]:
        """Get allowed methods as a list."""
        return [method.strip() for method in self.allowed_methods.split(",") if method.strip()]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",") if file_type.strip()]
    
    def get_database_url(self, *, async_driver: bool = True) -> str:
        """Get database URL with appropriate driver."""
        if async_driver and "postgresql://" in self.database_url:
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


# Environment-specific configurations
def get_azure_openai_config() -> dict:
    """Get Azure OpenAI configuration."""
    return {
        "azure_endpoint": settings.azure_openai_endpoint,
        "api_key": settings.azure_openai_api_key,
        "api_version": settings.azure_openai_api_version,
        "azure_deployment": settings.azure_openai_deployment_name,
        "model": settings.azure_openai_model_name,
    }


def get_cors_config() -> dict:
    """Get CORS configuration."""
    return {
        "allow_origins": settings.allowed_origins_list,
        "allow_credentials": True,
        "allow_methods": settings.allowed_methods_list,
        "allow_headers": [settings.allowed_headers],
    }


def get_security_config() -> dict:
    """Get security configuration."""
    return {
        "secret_key": settings.secret_key,
        "algorithm": settings.algorithm,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
        "refresh_token_expire_days": settings.refresh_token_expire_days,
    }

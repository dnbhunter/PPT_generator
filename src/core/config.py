"""Configuration settings for DNB Presentation Generator."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Configuration
    app_name: str = "DNB Presentation Generator"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    worker_processes: int = 1
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production-12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./presentations.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Azure Configuration (Mock for development)
    azure_tenant_id: str = "mock-tenant-id"
    azure_client_id: str = "mock-client-id"
    azure_client_secret: str = "mock-client-secret"
    azure_subscription_id: str = "mock-subscription-id"
    azure_resource_group: str = "mock-rg"
    
    # Azure OpenAI Configuration (Mock for development)
    azure_openai_endpoint: str = "https://mock-openai.openai.azure.com/"
    azure_openai_api_key: str = "mock-api-key"
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_model_name: str = "gpt-4o"
    
    # Azure Key Vault Configuration
    azure_key_vault_url: str = "https://mock-keyvault.vault.azure.net/"
    
    # File Upload Configuration
    max_file_size: str = "50MB"
    allowed_file_types: str = ".pdf,.docx,.txt,.md"
    upload_directory: str = "./uploads"
    
    # Presentation Configuration
    max_slides_per_presentation: int = 25
    default_template: str = "corporate"
    chart_generation_enabled: bool = True
    image_search_enabled: bool = False
    
    # Compliance Configuration
    pii_detection_enabled: bool = False
    content_safety_enabled: bool = False
    audit_logging_enabled: bool = True
    data_retention_days: int = 30
    
    # Performance Configuration
    max_concurrent_requests: int = 50
    request_timeout_seconds: int = 60
    cache_ttl_seconds: int = 300
    
    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Feature Flags
    enable_experimental_features: bool = True
    enable_advanced_charts: bool = False
    enable_ai_suggestions: bool = False
    enable_collaborative_editing: bool = False
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 20
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get allowed CORS origins."""
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
    
    @property
    def allowed_methods(self) -> List[str]:
        """Get allowed CORS methods."""
        return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    @property
    def allowed_headers(self) -> List[str]:
        """Get allowed CORS headers."""
        return ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_cors_config():
    """Get CORS configuration."""
    settings = get_settings()
    return {
        "allow_origins": settings.allowed_origins,
        "allow_credentials": True,
        "allow_methods": settings.allowed_methods,
        "allow_headers": settings.allowed_headers,
    }


def get_azure_openai_config():
    """Get Azure OpenAI configuration."""
    settings = get_settings()
    return {
        "azure_endpoint": settings.azure_openai_endpoint,
        "api_key": settings.azure_openai_api_key,
        "api_version": settings.azure_openai_api_version,
        "azure_deployment": settings.azure_openai_deployment_name,
        "model": settings.azure_openai_model_name,
    }


# Export settings instance
settings = get_settings()

"""Logging configuration for DNB Presentation Generator."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from structlog.stdlib import LoggerFactory

from .config import get_settings


settings = get_settings()


def setup_logging():
    """Setup structured logging configuration."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Get logging configuration
    logging_config = get_logging_config()
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Set root logger level
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))
    
    # Configure specific loggers
    configure_specific_loggers()


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration dictionary."""
    
    log_format = {
        "development": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "production": "%(message)s",  # JSON format handled by structlog
    }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": log_format.get(settings.environment, log_format["production"]),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level.upper(),
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "dnb_presentation": {
                "level": settings.log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level.upper(),
            "handlers": ["console", "file", "error_file"],
        },
    }


def configure_specific_loggers():
    """Configure specific loggers for different components."""
    
    # Suppress noisy third-party loggers in production
    if settings.is_production:
        logging.getLogger("azure").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)
    
    # Set specific levels for application components
    logging.getLogger("src.agents").setLevel(logging.INFO)
    logging.getLogger("src.services").setLevel(logging.INFO)
    logging.getLogger("src.security").setLevel(logging.WARNING)
    logging.getLogger("src.api").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

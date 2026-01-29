"""
Configuration management for the Todo application.

This module uses Pydantic Settings to load and validate environment variables
from the .env file. All configuration is centralized here for easy access
throughout the application.

Usage:
    from app.config import settings

    # Access configuration
    database_url = settings.DATABASE_URL
    secret_key = settings.BETTER_AUTH_SECRET
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from the .env file in the backend directory.
    Required settings will raise a validation error if not provided.
    """

    # ========================================
    # Database Configuration
    # ========================================

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection string (async format)",
        examples=["postgresql+psycopg://user:pass@host:5432/dbname"]
    )

    # ========================================
    # Authentication Configuration
    # ========================================

    BETTER_AUTH_SECRET: str = Field(
        ...,
        description="Secret key for JWT token signing (must be kept secure)",
        min_length=32
    )

    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT token encoding/decoding"
    )

    JWT_EXPIRY_DAYS: int = Field(
        default=7,
        description="Number of days before JWT tokens expire",
        ge=1,
        le=365
    )

    # ========================================
    # CORS Configuration
    # ========================================

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # ========================================
    # Server Configuration
    # ========================================

    SERVER_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for the server to bind to"
    )

    SERVER_PORT: int = Field(
        default=8001,
        description="Port number for the server to listen on",
        ge=1024,
        le=65535
    )

    # ========================================
    # Application Configuration
    # ========================================

    APP_NAME: str = Field(
        default="Todo API",
        description="Application name for documentation"
    )

    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (SQL logging, detailed errors)"
    )

    # ========================================
    # Pydantic Settings Configuration
    # ========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )

    # ========================================
    # Validators
    # ========================================

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Validate that DATABASE_URL is properly formatted.

        Args:
            v: Database URL string

        Returns:
            Validated database URL

        Raises:
            ValueError: If URL format is invalid
        """
        if not v.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+psycopg://'"
            )
        return v

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """
        Validate CORS origins format.

        Args:
            v: Comma-separated CORS origins

        Returns:
            Validated CORS origins string
        """
        # Split and validate each origin
        origins = [origin.strip() for origin in v.split(",")]
        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"Invalid CORS origin '{origin}'. Must start with http:// or https://"
                )
        return v

    # ========================================
    # Helper Methods
    # ========================================

    def get_cors_origins_list(self) -> List[str]:
        """
        Get CORS origins as a list.

        Returns:
            List of allowed CORS origin URLs
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def is_production(self) -> bool:
        """
        Check if running in production mode.

        Returns:
            True if not in debug mode
        """
        return not self.DEBUG


# ========================================
# Global Settings Instance
# ========================================

# Create a single instance of settings to be imported throughout the app
# This ensures configuration is loaded once and reused
settings = Settings()


# ========================================
# Configuration Validation on Import
# ========================================

def validate_settings() -> None:
    """
    Validate critical settings on application startup.

    This function performs additional validation beyond Pydantic's
    automatic validation to ensure the application is properly configured.

    Raises:
        ValueError: If any critical configuration is invalid
    """
    # Validate JWT secret strength
    if len(settings.BETTER_AUTH_SECRET) < 32:
        raise ValueError(
            "BETTER_AUTH_SECRET must be at least 32 characters long for security"
        )

    # Validate database URL contains required components
    if "@" not in settings.DATABASE_URL or "/" not in settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL appears to be malformed. "
            "Expected format: postgresql://user:pass@host:port/dbname"
        )

    # Warn if running in debug mode
    if settings.DEBUG:
        print("⚠️  WARNING: Running in DEBUG mode. Disable in production!")


# Run validation on import
validate_settings()

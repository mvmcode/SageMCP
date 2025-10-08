"""Configuration management for Sage MCP."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Sage MCP"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://sage_mcp:password@localhost:5432/sage_mcp",
        env="DATABASE_URL"
    )

    # Security
    secret_key: str = Field(env="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7, env="REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # OAuth Configuration
    github_client_id: Optional[str] = Field(
        default=None, env="GITHUB_CLIENT_ID"
    )
    github_client_secret: Optional[str] = Field(
        default=None, env="GITHUB_CLIENT_SECRET"
    )

    gitlab_client_id: Optional[str] = Field(
        default=None, env="GITLAB_CLIENT_ID"
    )
    gitlab_client_secret: Optional[str] = Field(
        default=None, env="GITLAB_CLIENT_SECRET"
    )

    google_client_id: Optional[str] = Field(
        default=None, env="GOOGLE_CLIENT_ID"
    )
    google_client_secret: Optional[str] = Field(
        default=None, env="GOOGLE_CLIENT_SECRET"
    )

    # Base URL for OAuth redirects
    base_url: str = Field(default="http://localhost:8000", env="BASE_URL")

    # MCP Configuration
    mcp_server_timeout: int = Field(default=30, env="MCP_SERVER_TIMEOUT")
    mcp_max_connections_per_tenant: int = Field(
        default=10, env="MCP_MAX_CONNECTIONS_PER_TENANT"
    )

    @validator("secret_key", pre=True)
    def validate_secret_key(cls, v):
        if not v:
            # Generate a random secret key for development
            import secrets
            return secrets.token_urlsafe(32)
        return v

    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if isinstance(v, str):
            return v
        return str(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

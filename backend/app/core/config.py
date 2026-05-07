"""Environment-based settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for HTTP + gRPC servers."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg2://library:library@127.0.0.1:5433/neighborhood_library",
        description="SQLAlchemy URL (psycopg2 driver)",
    )
    grpc_host: str = Field(default="0.0.0.0")
    grpc_port: int = Field(default=50051, ge=1, le=65535)
    http_host: str = Field(default="0.0.0.0")
    http_port: int = Field(default=8000, ge=1, le=65535)

    default_loan_period_days: int = Field(default=14, ge=1, le=365)
    fine_cents_per_day: int = Field(default=50, ge=0)
    fine_grace_days: int = Field(default=0, ge=0)
    fine_currency_code: str = Field(default="USD", min_length=3, max_length=3)

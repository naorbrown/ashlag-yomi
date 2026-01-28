"""
Configuration management for Ashlag Yomi.

Uses Pydantic Settings for type-safe configuration loaded from environment
variables. This follows the 12-factor app principle of storing config in
the environment.

Usage:
    from src.utils.config import get_settings

    settings = get_settings()
    print(settings.telegram_bot_token)
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic Settings automatically:
    - Loads from .env file (if python-dotenv is installed)
    - Converts types (str -> int, etc.)
    - Validates required fields
    - Keeps secrets secure (SecretStr masks in logs)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )

    # =========================================================================
    # Telegram Configuration (Required)
    # =========================================================================

    telegram_bot_token: SecretStr = Field(
        ...,  # Required field
        description="Bot token from @BotFather",
    )

    telegram_chat_id: str = Field(
        ...,  # Required field
        description="Channel/group ID where quotes are posted",
    )

    telegram_channel_id: str | None = Field(
        default=None,
        description="Optional public channel ID (e.g., @AshlagYomi) for daily broadcasts",
    )

    # =========================================================================
    # Application Settings
    # =========================================================================

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Runtime environment",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging verbosity",
    )

    # =========================================================================
    # Optional Settings
    # =========================================================================

    sentry_dsn: SecretStr | None = Field(
        default=None,
        description="Sentry DSN for error tracking",
    )

    daily_send_time: str = Field(
        default="06:00",
        description="Time to send daily quotes (HH:MM, Israel timezone)",
    )

    dry_run: bool = Field(
        default=False,
        description="If True, log messages instead of sending",
    )

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once per process.
    This is important because loading from .env file has I/O overhead.

    Returns:
        Settings: Validated application settings

    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return Settings()

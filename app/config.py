"""Configuration placeholder for DevFlow Agent."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Minimal settings model for baseline repository setup."""

    app_name: str = "DevFlow Agent"
    environment: str = "development"

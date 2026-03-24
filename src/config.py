"""Configuration loading for the Garmin strength MVP scaffold."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Application settings sourced from environment variables."""

    garmin_email: str | None
    garmin_password: str | None
    sqlite_path: Path


def load_settings() -> Settings:
    """Load application settings from environment variables.

    Environment variables:
        GARMIN_EMAIL: Optional Garmin account email for future integration.
        GARMIN_PASSWORD: Optional Garmin account password for future integration.
        SQLITE_PATH: Optional path to SQLite database file.
    """

    sqlite_path = Path(os.getenv("SQLITE_PATH", "data/garmin_strength.db"))
    return Settings(
        garmin_email=os.getenv("GARMIN_EMAIL"),
        garmin_password=os.getenv("GARMIN_PASSWORD"),
        sqlite_path=sqlite_path,
    )

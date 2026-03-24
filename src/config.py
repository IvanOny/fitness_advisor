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
    garmin_tokenstore: Path
    sqlite_path: Path


def load_settings() -> Settings:
    """Load application settings from environment variables.

    Environment variables:
        GARMIN_EMAIL: Garmin account email.
        GARMIN_PASSWORD: Garmin account password.
        GARMIN_TOKENSTORE: Optional path used to persist Garmin auth tokens.
        SQLITE_PATH: Optional path to SQLite database file.
    """

    sqlite_path = Path(os.getenv("SQLITE_PATH", "data/garmin_strength.db"))
    garmin_tokenstore = Path(os.getenv("GARMIN_TOKENSTORE", "data/.garmin_tokens"))
    return Settings(
        garmin_email=os.getenv("GARMIN_EMAIL"),
        garmin_password=os.getenv("GARMIN_PASSWORD"),
        garmin_tokenstore=garmin_tokenstore,
        sqlite_path=sqlite_path,
    )

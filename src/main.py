"""Entry point for the Garmin strength MVP scaffold."""

from __future__ import annotations

from config import load_settings
from db import initialize_database


def main() -> None:
    """Load configuration, initialize SQLite, and print scaffold status."""

    settings = load_settings()
    initialize_database(settings.sqlite_path)
    print("Garmin strength MVP scaffold ready.")


if __name__ == "__main__":
    main()

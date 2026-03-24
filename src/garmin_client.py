"""Stub Garmin client for future Garmin Connect integration."""

from __future__ import annotations


class GarminClient:
    """Placeholder Garmin API client.

    This class intentionally does not perform any real authentication yet.
    """

    def __init__(self, email: str | None = None, password: str | None = None) -> None:
        """Store credentials for future use."""

        self.email = email
        self.password = password

    def is_configured(self) -> bool:
        """Return True when both email and password are present."""

        return bool(self.email and self.password)

    def fetch_strength_workouts(self) -> list[dict]:
        """Return an empty list placeholder for future strength workout retrieval."""

        return []

    def fetch_recovery_data(self) -> dict:
        """Return an empty placeholder for future recovery data retrieval."""

        return {}

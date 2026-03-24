"""Small Garmin Connect client wrapper for smoke tests and data inspection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


class GarminClientError(RuntimeError):
    """Raised when Garmin operations fail in a user-facing way."""


@dataclass(slots=True)
class GarminClient:
    """Minimal wrapper around python-garminconnect with readable errors."""

    email: str
    password: str
    tokenstore_path: Path
    _api: Any = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.tokenstore_path = self.tokenstore_path.expanduser()

    def login(self) -> None:
        """Authenticate with Garmin Connect and initialize the underlying API client."""

        try:
            from garminconnect import (
                Garmin,
                GarminConnectAuthenticationError,
                GarminConnectConnectionError,
                GarminConnectTooManyRequestsError,
            )
        except ImportError as exc:
            raise GarminClientError(
                "Missing dependency: garminconnect. Run `pip install -r requirements.txt`."
            ) from exc

        self.tokenstore_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            api = Garmin()
            api.login(str(self.tokenstore_path))
            self._api = api
            return
        except FileNotFoundError:
            pass
        except GarminConnectAuthenticationError:
            pass
        except GarminConnectConnectionError as exc:
            raise GarminClientError(
                f"Could not reach Garmin Connect using cached tokens: {exc}"
            ) from exc

        if not self.email or not self.password:
            raise GarminClientError(
                "Missing GARMIN_EMAIL or GARMIN_PASSWORD. Set both to perform initial login."
            )

        try:
            api = Garmin(email=self.email, password=self.password)
            api.login()
            if hasattr(api, "garth"):
                api.garth.dump(str(self.tokenstore_path))
            self._api = api
        except GarminConnectAuthenticationError as exc:
            raise GarminClientError(
                "Garmin authentication failed. Double-check GARMIN_EMAIL/GARMIN_PASSWORD."
            ) from exc
        except GarminConnectTooManyRequestsError as exc:
            raise GarminClientError(
                "Garmin rate-limited this request (too many attempts). Try again later."
            ) from exc
        except GarminConnectConnectionError as exc:
            raise GarminClientError(f"Could not reach Garmin Connect: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 - keep wrapper readable and small
            raise GarminClientError(f"Unexpected Garmin login error: {exc}") from exc

    def get_profile(self) -> dict[str, Any]:
        """Return a lightweight account payload for smoke-test verification."""

        api = self._require_api()
        try:
            full_name = api.get_full_name()
            device_last_used = api.get_device_last_used()
        except Exception as exc:  # noqa: BLE001
            raise GarminClientError(f"Failed to fetch Garmin profile data: {exc}") from exc

        return {
            "full_name": full_name,
            "device_last_used": device_last_used,
        }

    def get_recent_activities(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return recent Garmin activities (most recent first)."""

        api = self._require_api()
        try:
            activities = api.get_activities(0, limit)
        except Exception as exc:  # noqa: BLE001
            raise GarminClientError(f"Failed to fetch recent Garmin activities: {exc}") from exc

        if not isinstance(activities, list):
            raise GarminClientError("Garmin activities response was not a list as expected.")
        return activities

    def get_daily_summary(self, for_date: date | None = None) -> dict[str, Any]:
        """Return a minimal daily summary payload for a single date."""

        api = self._require_api()
        query_date = (for_date or date.today()).isoformat()

        try:
            return api.get_user_summary(query_date)
        except Exception as exc:  # noqa: BLE001
            raise GarminClientError(
                f"Failed to fetch daily summary for {query_date}: {exc}"
            ) from exc

    def _require_api(self) -> Any:
        if self._api is None:
            raise GarminClientError("Not logged in. Call login() before requesting data.")
        return self._api

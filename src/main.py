"""CLI entry point for Garmin smoke-testing and basic data inspection."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from .config import load_settings
from .garmin_client import GarminClient, GarminClientError


def _write_json(path: Path, payload: Any) -> None:
    """Write JSON payload in a stable, human-inspectable format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def _build_client() -> GarminClient:
    settings = load_settings()
    return GarminClient(
        email=settings.garmin_email or "",
        password=settings.garmin_password or "",
        tokenstore_path=settings.garmin_tokenstore,
    )


def run_smoke_test() -> int:
    """Authenticate and fetch one lightweight account endpoint."""

    client = _build_client()
    try:
        client.login()
        profile = client.get_profile()
    except GarminClientError as exc:
        print(f"❌ Smoke test failed: {exc}")
        return 1

    name = profile.get("full_name") or "<unknown>"
    print("✅ Smoke test passed.")
    print(f"Logged in as: {name}")
    return 0


def run_recent_activities(limit: int = 10) -> int:
    """Fetch recent activities, print summary, and save raw JSON."""

    client = _build_client()
    try:
        client.login()
        activities = client.get_recent_activities(limit=limit)
    except GarminClientError as exc:
        print(f"❌ recent-activities failed: {exc}")
        return 1

    for idx, activity in enumerate(activities, start=1):
        activity_name = activity.get("activityName", "<unnamed>")
        activity_type = activity.get("activityType", {}).get("typeKey", "unknown")
        start_time = activity.get("startTimeLocal", "unknown")
        duration_seconds = activity.get("duration", "unknown")
        print(
            f"{idx:>2}. {start_time} | {activity_type:>12} | "
            f"{duration_seconds:>8} sec | {activity_name}"
        )

    output_path = Path("data/recent_activities.json")
    _write_json(output_path, activities)
    print(f"Saved raw JSON to {output_path}")
    return 0


def run_daily_summary() -> int:
    """Fetch today's Garmin daily summary and save raw JSON."""

    client = _build_client()
    today = date.today()
    try:
        client.login()
        summary = client.get_daily_summary(today)
    except GarminClientError as exc:
        print(f"❌ daily-summary failed: {exc}")
        return 1

    output_path = Path("data/daily_summary.json")
    _write_json(output_path, summary)
    print(f"Saved daily summary for {today.isoformat()} to {output_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser for supported modes."""

    parser = argparse.ArgumentParser(description="Garmin strength MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("smoke-test", help="Login and fetch lightweight profile data")

    recent_parser = subparsers.add_parser(
        "recent-activities", help="Fetch recent activities and save raw JSON"
    )
    recent_parser.add_argument("--limit", type=int, default=10, help="Number of activities")

    subparsers.add_parser("daily-summary", help="Fetch one-day user summary JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the selected CLI mode."""

    args = build_parser().parse_args(argv)

    if args.command == "smoke-test":
        return run_smoke_test()
    if args.command == "recent-activities":
        return run_recent_activities(limit=args.limit)
    if args.command == "daily-summary":
        return run_daily_summary()

    print(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

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


def _iter_nodes(payload: Any) -> Any:
    """Yield all nested JSON nodes in a payload."""

    yield payload
    if isinstance(payload, dict):
        for value in payload.values():
            yield from _iter_nodes(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_nodes(item)


def _find_strength_activities(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter activities that look like strength workouts."""

    strength_hints = ("strength", "weight", "gym")
    filtered: list[dict[str, Any]] = []

    for activity in activities:
        type_key = str(activity.get("activityType", {}).get("typeKey", "")).lower()
        name = str(activity.get("activityName", "")).lower()
        if any(hint in type_key for hint in strength_hints) or any(
            hint in name for hint in strength_hints
        ):
            filtered.append(activity)
    return filtered


def _is_bench_press_name(value: str) -> bool:
    query = value.lower()
    patterns = ("bench", "bench press", "barbell bench", "Barbell Bench Press")
    return any(pattern in query for pattern in patterns)


def _extract_sets(candidate: Any) -> list[dict[str, Any]]:
    """Extract set-like dictionaries from a candidate payload node."""

    sets: list[dict[str, Any]] = []
    for node in _iter_nodes(candidate):
        if not isinstance(node, dict):
            continue
        keys = {str(k).lower() for k in node.keys()}
        has_reps = any("rep" in key for key in keys)
        has_weight = any("weight" in key or "kg" in key or "lb" in key for key in keys)
        if has_reps and has_weight:
            sets.append(node)
    return sets


def _first_value_by_key_hint(payload: dict[str, Any], hints: tuple[str, ...]) -> Any:
    for key, value in payload.items():
        if any(hint in str(key).lower() for hint in hints):
            return value
    return None


def _print_set_summary(sets: list[dict[str, Any]]) -> None:
    if not sets:
        print("Sets summary: no obvious set/rep/weight fields found")
        return

    print("Sets summary:")
    for idx, item in enumerate(sets[:3], start=1):
        reps = _first_value_by_key_hint(item, ("rep",))
        weight = _first_value_by_key_hint(item, ("weight", "kg", "lb"))
        if reps is None:
            reps = "?"
        if weight is None:
            weight = "?"
        print(f"Set {idx}: {weight} x {reps}")


def _scan_payload_for_exercise(payload: dict[str, Any]) -> tuple[str, Any, list[dict[str, Any]]] | None:
    """
    Recursively scan activity detail payload for a bench press exercise-like structure.

    Returns exercise name, matched subsection, and extracted set-like rows.
    """

    for node in _iter_nodes(payload):
        if not isinstance(node, dict):
            continue

        for key, value in node.items():
            if not isinstance(value, str):
                continue
            key_name = str(key).lower()
            if "name" not in key_name and "exercise" not in key_name:
                continue
            if _is_bench_press_name(value):
                return value, node, _extract_sets(node)
    return None


def run_inspect_bench_press() -> int:
    """Inspect recent strength workouts for barbell bench press exercise structures."""

    client = _build_client()
    try:
        client.login()
        activities = client.get_recent_activities(limit=50)
    except GarminClientError as exc:
        print(f"❌ inspect-bench-press failed: {exc}")
        return 1

    strength_activities = _find_strength_activities(activities)
    if not strength_activities:
        print("No strength-like activities found in recent history.")
        return 0

    max_inspections = min(len(strength_activities), 6)
    found = False

    for index, activity in enumerate(strength_activities[:max_inspections], start=1):
        activity_id = activity.get("activityId")
        if activity_id is None:
            continue

        try:
            detail = client.get_activity_detail(int(activity_id))
        except GarminClientError as exc:
            print(f"⚠️ Skipping activity {activity_id}: {exc}")
            continue

        raw_output = Path(f"data/strength_activity_{activity_id}.json")
        _write_json(raw_output, detail)
        print(f"Inspected strength workout {index}/{max_inspections}: saved {raw_output}")

        matched = _scan_payload_for_exercise(detail)
        if not matched:
            continue

        exercise_name, subsection, sets = matched
        print("")
        print(f"Activity ID: {activity_id}")
        print(f"Date: {activity.get('startTimeLocal', 'unknown')}")
        print(f"Activity name: {activity.get('activityName', '<unnamed>')}")
        print("")
        print(f"Exercise detected: {exercise_name}")
        _print_set_summary(sets)

        _write_json(Path("data/bench_press_detected.json"), subsection)
        print("Saved matched subsection to data/bench_press_detected.json")
        found = True
        break

    if not found:
        print("No barbell bench press exercise detected in the last 5 strength workouts.")
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
    subparsers.add_parser(
        "inspect-bench-press",
        help="Inspect recent strength workouts for bench press exercise payloads",
    )
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
    if args.command == "inspect-bench-press":
        return run_inspect_bench_press()

    print(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

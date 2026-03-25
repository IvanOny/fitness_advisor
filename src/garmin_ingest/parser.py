from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fitparse import FitFile

MESSAGE_TYPES = ("session", "lap", "record", "event", "set")


@dataclass
class ParsedFitPayload:
    files_processed: int
    sessions_raw: list[dict[str, Any]]
    laps_raw: list[dict[str, Any]]
    records_raw: list[dict[str, Any]]
    events_raw: list[dict[str, Any]]
    sets_raw: list[dict[str, Any]]
    parse_errors: list[str]


def _extract_message_fields(message: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for field in message:
        if field is None:
            continue
        value = getattr(field, "value", None)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        fields[field.name] = value
    return fields


def _parse_fit_file(file_path: Path) -> dict[str, list[dict[str, Any]]]:
    fitfile = FitFile(str(file_path))

    parsed: dict[str, list[dict[str, Any]]] = {name: [] for name in MESSAGE_TYPES}
    for message_type in MESSAGE_TYPES:
        for message in fitfile.get_messages(message_type):
            row = {
                "source_file": file_path.name,
                "source_path": str(file_path),
                "message_type": message_type,
            }
            row.update(_extract_message_fields(message))
            parsed[message_type].append(row)
    return parsed


def parse_fit_directory(input_dir: Path) -> ParsedFitPayload:
    fit_paths = sorted(input_dir.glob("*.fit")) + sorted(input_dir.glob("*.FIT"))

    sessions_raw: list[dict[str, Any]] = []
    laps_raw: list[dict[str, Any]] = []
    records_raw: list[dict[str, Any]] = []
    events_raw: list[dict[str, Any]] = []
    sets_raw: list[dict[str, Any]] = []
    parse_errors: list[str] = []

    for fit_path in fit_paths:
        try:
            parsed_file = _parse_fit_file(fit_path)
        except Exception as exc:  # noqa: BLE001
            parse_errors.append(f"{fit_path.name}: {exc}")
            continue

        sessions_raw.extend(parsed_file["session"])
        laps_raw.extend(parsed_file["lap"])
        records_raw.extend(parsed_file["record"])
        events_raw.extend(parsed_file["event"])
        sets_raw.extend(parsed_file["set"])

    return ParsedFitPayload(
        files_processed=len(fit_paths),
        sessions_raw=sessions_raw,
        laps_raw=laps_raw,
        records_raw=records_raw,
        events_raw=events_raw,
        sets_raw=sets_raw,
        parse_errors=parse_errors,
    )

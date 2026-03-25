from __future__ import annotations

from typing import Any

import pandas as pd

from .parser import ParsedFitPayload


def _normalize_rows(rows: list[dict[str, Any]], preferred_columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=preferred_columns)

    df = pd.DataFrame(rows)
    for column in preferred_columns:
        if column not in df.columns:
            df[column] = pd.NA

    ordered_existing = [column for column in preferred_columns if column in df.columns]
    remainder = [column for column in df.columns if column not in ordered_existing]
    return df[ordered_existing + remainder]


def normalize_fit_payload(payload: ParsedFitPayload) -> dict[str, pd.DataFrame]:
    sessions_df = _normalize_rows(
        payload.sessions_raw,
        preferred_columns=[
            "source_file",
            "sport",
            "sub_sport",
            "start_time",
            "timestamp",
            "total_timer_time",
            "total_elapsed_time",
            "total_calories",
            "total_distance",
        ],
    )

    laps_df = _normalize_rows(
        payload.laps_raw,
        preferred_columns=[
            "source_file",
            "sport",
            "sub_sport",
            "start_time",
            "timestamp",
            "total_timer_time",
            "total_elapsed_time",
            "total_calories",
            "total_distance",
        ],
    )

    records_df = _normalize_rows(
        payload.records_raw,
        preferred_columns=[
            "source_file",
            "timestamp",
            "heart_rate",
            "cadence",
            "distance",
            "enhanced_speed",
            "enhanced_altitude",
            "position_lat",
            "position_long",
        ],
    )

    sets_df = _normalize_rows(
        payload.sets_raw,
        preferred_columns=[
            "source_file",
            "timestamp",
            "set_type",
            "weight",
            "repetitions",
            "duration",
            "category",
            "exercise_category",
            "wkt_step_name",
        ],
    )

    events_df = _normalize_rows(
        payload.events_raw,
        preferred_columns=[
            "source_file",
            "timestamp",
            "event",
            "event_type",
            "data",
            "timer_trigger",
        ],
    )

    return {
        "sessions_df": sessions_df,
        "laps_df": laps_df,
        "records_df": records_df,
        "sets_df": sets_df,
        "events_df": events_df,
    }

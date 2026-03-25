from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

BENCH_HINTS = ("bench", "bench press", "barbell bench press")


def get_io_paths(input_arg: str | None, output_arg: str | None) -> tuple[Path, Path]:
    input_dir = Path(input_arg or os.getenv("GARMIN_FIT_INPUT", "data/input"))
    output_dir = Path(output_arg or os.getenv("GARMIN_FIT_OUTPUT", "data/output"))
    return input_dir, output_dir


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_dataframes(frames: dict[str, pd.DataFrame], output_dir: Path) -> None:
    name_map = {
        "sessions_df": "sessions.csv",
        "laps_df": "laps.csv",
        "records_df": "records.csv",
        "sets_df": "sets.csv",
        "events_df": "events.csv",
    }
    for key, filename in name_map.items():
        frames[key].to_csv(output_dir / filename, index=False)


def detect_bench_press_sets(sets_df: pd.DataFrame) -> tuple[bool, pd.DataFrame, list[str]]:
    if sets_df.empty:
        return False, sets_df, []

    candidate_cols = [
        column
        for column in sets_df.columns
        if any(token in column.lower() for token in ("exercise", "name", "category", "workout", "step"))
    ]

    if not candidate_cols:
        return False, sets_df.iloc[0:0], []

    mask = pd.Series(False, index=sets_df.index)
    for column in candidate_cols:
        col_values = sets_df[column].astype(str).str.lower()
        mask = mask | col_values.apply(lambda value: any(hint in value for hint in BENCH_HINTS))

    matched = sets_df[mask].copy()
    return not matched.empty, matched, candidate_cols

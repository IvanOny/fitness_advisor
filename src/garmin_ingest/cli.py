from __future__ import annotations

import argparse
from pathlib import Path

from .normalize import normalize_fit_payload
from .parser import parse_fit_directory
from .utils import detect_bench_press_sets, ensure_output_dir, get_io_paths, save_dataframes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse Garmin FIT files into normalized CSV outputs.")
    parser.add_argument("--input", type=str, default=None, help="Input folder with .fit files")
    parser.add_argument("--output", type=str, default=None, help="Output folder for CSV files")
    return parser


def run(input_dir: Path, output_dir: Path) -> int:
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return 1

    ensure_output_dir(output_dir)

    parsed_payload = parse_fit_directory(input_dir)
    frames = normalize_fit_payload(parsed_payload)
    save_dataframes(frames, output_dir)

    sessions_df = frames["sessions_df"]
    sets_df = frames["sets_df"]

    latest_strength_sets = sets_df
    if not sessions_df.empty and "sport" in sessions_df.columns and "start_time" in sessions_df.columns:
        sessions_ordered = sessions_df.sort_values(by="start_time", ascending=False, na_position="last")
        strength_rows = sessions_ordered[
            sessions_ordered["sport"].astype(str).str.lower().str.contains("strength", na=False)
        ]
        if not strength_rows.empty:
            latest_source = strength_rows.iloc[0].get("source_file")
            if "source_file" in sets_df.columns:
                latest_strength_sets = sets_df[sets_df["source_file"] == latest_source]

    found_bench, matched_rows, candidate_fields = detect_bench_press_sets(latest_strength_sets)

    print("=== Garmin FIT ingest summary ===")
    print(f"FIT files discovered: {parsed_payload.files_processed}")
    print(f"Sessions extracted: {len(sessions_df)}")
    print(f"Sets extracted: {len(sets_df)}")
    print(f"Bench press likely found: {'yes' if found_bench else 'no'}")
    if candidate_fields:
        print(f"Bench detection fields inspected: {', '.join(candidate_fields)}")
    if not matched_rows.empty:
        print(f"Bench-like set rows matched: {len(matched_rows)}")
    if parsed_payload.parse_errors:
        print("Parse errors:")
        for err in parsed_payload.parse_errors:
            print(f"  - {err}")

    return 0


def main() -> int:
    args = build_parser().parse_args()
    input_dir, output_dir = get_io_paths(args.input, args.output)
    return run(input_dir, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())

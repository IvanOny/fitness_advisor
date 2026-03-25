# Garmin FIT Ingestion (MVP)

This project parses Garmin-exported `.fit` workout files from a local folder and converts them into normalized pandas DataFrames for downstream fitness analysis.

Pipeline:

`FIT files -> raw extraction layer -> normalization layer -> CSV outputs`

## Why this parser stack

This MVP uses:
- `fitparse` for FIT file parsing
- `pandas` for normalization and CSV output

`fitparse` is lightweight and practical for local development workflows.

## Project structure

```text
src/
  garmin_ingest/
    __init__.py
    parser.py
    normalize.py
    cli.py
    utils.py
data/
  input/
  output/
requirements.txt
README.md
```

## Setup

1. Create and activate a Python environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## CLI usage

From repository root:

```bash
PYTHONPATH=src python -m garmin_ingest.cli --input ./data/input --output ./data/output
```

If CLI args are omitted, defaults can come from environment variables:
- `GARMIN_FIT_INPUT` (default: `data/input`)
- `GARMIN_FIT_OUTPUT` (default: `data/output`)

Example with env vars:

```bash
export GARMIN_FIT_INPUT=./data/input
export GARMIN_FIT_OUTPUT=./data/output
PYTHONPATH=src python -m garmin_ingest.cli
```

## What the CLI does

1. Finds all `.fit` / `.FIT` files in the input directory.
2. Parses message types when present: `session`, `lap`, `record`, `event`, `set`.
3. Builds normalized DataFrames:
   - `sessions_df`
   - `laps_df`
   - `records_df`
   - `sets_df`
   - `events_df`
4. Saves CSVs to output folder:
   - `sessions.csv`
   - `laps.csv`
   - `records.csv`
   - `sets.csv`
   - `events.csv`
5. Prints summary:
   - number of FIT files processed
   - number of sessions
   - number of sets
   - whether bench-press-like data was detected

## Strength and bench-press detection notes

- Strength workouts often carry useful data in `set` messages, not only `record` messages.
- This MVP explicitly parses `set` messages and prioritizes them for exercise detection.
- Bench detection currently uses case-insensitive string matching against values containing:
  - `bench`
  - `bench press`
  - `barbell bench press`
- If exact exercise names are missing, the tool prints candidate columns inspected (for easy iterative improvement).
- Current behavior checks the latest detected strength workout first; the code is structured so extending to previous workouts is straightforward.

## Known limitations

- Garmin FIT strength schemas vary by device, app version, and export source.
- Some files may omit message types (`set`, `lap`, etc.) entirely.
- Field naming for exercises can vary; this version intentionally preserves raw fields and avoids aggressive early normalization.
- Parse failures are collected and printed, while remaining files continue processing.

## Next suggested step

Inspect `sets.csv` and candidate exercise-related fields from your own exports, then tighten mapping logic for exercise names and set semantics.

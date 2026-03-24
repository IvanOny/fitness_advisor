# Garmin Strength Analysis MVP

## Purpose
A small, machine-independent MVP to verify Garmin Connect authentication and basic data fetches from a terminal.

## Scope (Current Step)
Implemented now:
- Garmin login smoke test,
- recent activity fetch + raw JSON dump,
- optional daily summary fetch + raw JSON dump,
- token cache path support via environment variable.

Still not implemented (by design):
- workout-set normalization,
- strength analysis,
- charts,
- OpenAI integration,
- CI workflow expansion.

## Requirements
- Python 3.11

## Dependencies
Install with:

```bash
pip install -r requirements.txt
```

Current runtime dependency:
- `garminconnect`

## Environment Variables
Copy and edit:

```bash
cp .env.example .env
```

Required for initial login:
- `GARMIN_EMAIL`
- `GARMIN_PASSWORD`

Optional:
- `GARMIN_TOKENSTORE` (default: `data/.garmin_tokens`)
- `SQLITE_PATH` (default: `data/garmin_strength.db`)

> In Codespaces/Codex cloud, you can export these in the terminal session instead of using `.env`.

## CLI Usage
Run commands from repo root.

### 1) Smoke test (login + lightweight profile fetch)

```bash
python -m src.main smoke-test
```

Expected behavior:
- authenticates with cached token if available,
- otherwise logs in using `GARMIN_EMAIL`/`GARMIN_PASSWORD`,
- prints clear success/failure status.

### 2) Recent activities

```bash
python -m src.main recent-activities
```

Optional count:

```bash
python -m src.main recent-activities --limit 5
```

Expected behavior:
- fetches recent Garmin activities,
- prints a compact terminal summary,
- saves raw payload to `data/recent_activities.json`.

### 3) Daily summary (optional inspection)

```bash
python -m src.main daily-summary
```

Expected behavior:
- fetches a one-day summary snapshot,
- saves raw payload to `data/daily_summary.json`.

### 4) Inspect bench press payloads in recent strength workouts

```bash
python -m src.main inspect-bench-press
```

Expected behavior:
- fetches recent activities and filters strength-like workouts,
- inspects the most recent strength workout first, then up to 5 previous strength workouts if needed,
- fetches and saves each inspected activity detail payload to `data/strength_activity_<activity_id>.json`,
- recursively scans payload content for exercise names matching bench press string hints,
- prints a compact set summary (`weight x reps`) for the first detected bench press entry,
- saves the matched subsection to `data/bench_press_detected.json`,
- stops early as soon as a bench press exercise is detected.

## Notes on Unofficial Garmin Access
This uses an unofficial Garmin Connect wrapper (`garminconnect`).

Limitations:
- Garmin may change endpoints or auth behavior without notice.
- MFA/challenge flows can occasionally require manual intervention.
- Rate limits and temporary server errors can occur.
- Data shapes can vary by account/device/region.

## Safety / Intended Use
For personal experimentation only.

Do not treat this as a production integration; it may break at any time if Garmin changes behavior.

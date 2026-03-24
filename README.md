# Garmin Strength Analysis MVP (Scaffold)

## Purpose
This repository is the initial scaffold for a machine-independent Garmin strength-analysis MVP.

The longer-term goal is to:
- fetch Garmin Connect recovery and strength workout data,
- normalize and store it,
- generate exercise progress summaries with recovery context.

## Current Status
This is **scaffold-only** and intentionally minimal.

Implemented today:
- project folder structure (`src/`, `tests/`, `data/`, `.devcontainer/`),
- configuration loading from environment variables,
- SQLite initialization with starter tables,
- stub Garmin client class (no real login),
- placeholder analysis functions,
- simple entrypoint that initializes DB and prints readiness.

Not implemented yet:
- real Garmin authentication and API calls,
- any OpenAI integration,
- dashboards/visualizations,
- robust test coverage,
- CI/CD automation.

## Requirements
- Python 3.11

## Environment Variables
Copy the example file and set values as needed:

```bash
cp .env.example .env
```

Supported variables:
- `GARMIN_EMAIL` (optional for now)
- `GARMIN_PASSWORD` (optional for now)
- `SQLITE_PATH` (optional, defaults to `data/garmin_strength.db`)

## Run in GitHub Codespaces
1. Open this repository in GitHub.
2. Click **Code** → **Codespaces** → **Create codespace on main branch**.
3. In the terminal:

```bash
pip install -r requirements.txt
python src/main.py
```

You should see:

```text
Garmin strength MVP scaffold ready.
```

## Run Locally
1. Ensure Python 3.11 is installed.
2. Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) create `.env` from `.env.example` and edit values.
5. Run:

```bash
python src/main.py
```

## Project Structure
```text
.
├── .devcontainer/
├── data/
├── src/
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

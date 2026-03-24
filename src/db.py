"""SQLite database helpers for the Garmin strength MVP scaffold."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Return a SQLite connection, creating parent directories as needed."""

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def initialize_database(db_path: Path) -> None:
    """Create initial tables for recovery, workouts, and exercise sets if missing."""

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_recovery (
                id INTEGER PRIMARY KEY,
                recovery_date TEXT NOT NULL,
                body_battery INTEGER,
                hrv_status TEXT,
                resting_heart_rate INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY,
                garmin_workout_id TEXT UNIQUE,
                workout_date TEXT NOT NULL,
                sport TEXT,
                duration_seconds INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exercise_sets (
                id INTEGER PRIMARY KEY,
                workout_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                set_number INTEGER,
                reps INTEGER,
                weight_kg REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(workout_id) REFERENCES workouts(id)
            )
            """
        )
        conn.commit()

"""Data models for the Garmin strength MVP scaffold."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DailyRecovery:
    """Simplified recovery model."""

    recovery_date: str
    body_battery: int | None = None
    hrv_status: str | None = None
    resting_heart_rate: int | None = None


@dataclass(slots=True)
class Workout:
    """Simplified workout model."""

    garmin_workout_id: str
    workout_date: str
    sport: str | None = None
    duration_seconds: int | None = None


@dataclass(slots=True)
class ExerciseSet:
    """Simplified exercise set model."""

    workout_id: int
    exercise_name: str
    set_number: int | None = None
    reps: int | None = None
    weight_kg: float | None = None

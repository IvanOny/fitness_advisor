"""Analysis placeholders for the Garmin strength MVP scaffold."""

from __future__ import annotations


def compare_exercise_progress(exercise_name: str) -> dict:
    """Return a placeholder progress summary for a given exercise."""

    return {
        "exercise_name": exercise_name,
        "status": "not_implemented",
        "message": "Exercise progress comparison is not implemented yet.",
    }


def summarize_recovery_context(recovery_date: str) -> dict:
    """Return a placeholder recovery context summary."""

    return {
        "recovery_date": recovery_date,
        "status": "not_implemented",
        "message": "Recovery context summarization is not implemented yet.",
    }

"""
AI Escape Room & Game Arena — Centralized Universal Scoring Engine
Deterministic Time-Based Scoring Formula:
    SCORE = max(0, 10000 - (elapsed_seconds * 10))

Properties:
- Fully deterministic: The exact same completion time produces the exact same score.
- Unsolved or game over attempts score 0.
- Telemetry payload preserves raw metrics (moves, mistakes, hints, lives_remaining).
"""

from typing import Dict, Any, Optional


class ScoringEngine:
    """Universal deterministic scoring engine for all Arena games."""

    BASE_SCORE = 10000
    TIME_PENALTY_PER_SECOND = 10

    @classmethod
    def compute_formula(cls, elapsed_seconds: int, solved: bool = True) -> int:
        """
        Universal formula:
            SCORE = max(0, 10000 - (elapsed_seconds * 10))
        """
        if not solved:
            return 0
        t = max(0, int(elapsed_seconds))
        penalty = t * cls.TIME_PENALTY_PER_SECOND
        return max(0, cls.BASE_SCORE - penalty)

    @classmethod
    def calculate_game_score(
        cls,
        game_id: str,
        solved: bool = True,
        time_seconds: int = 0,
        mistakes: int = 0,
        hints_used: int = 0,
        moves_count: int = 0,
        difficulty: str = "medium",
        **kwargs
    ) -> Dict[str, Any]:
        """Calculates deterministic score and standard telemetry breakdown."""
        elapsed = max(0, int(time_seconds))
        total_score = cls.compute_formula(elapsed, solved=solved)
        time_penalty = elapsed * cls.TIME_PENALTY_PER_SECOND if solved else 0

        return {
            "game_id": game_id,
            "solved": solved,
            "time_seconds": elapsed,
            "score": total_score,
            "score_breakdown": {
                "base_score": cls.BASE_SCORE if solved else 0,
                "time_penalty": time_penalty,
                "formula": "max(0, 10000 - (time_seconds * 10))" if solved else "0 (Unsolved)"
            },
            "telemetry": {
                "mistakes": mistakes,
                "hints_used": hints_used,
                "moves_count": moves_count,
                "difficulty_tier": difficulty,
                **kwargs
            }
        }

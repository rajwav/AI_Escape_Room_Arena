"""
Unit Tests for Centralized Deterministic Scoring Engine.
SCORE = max(0, 10000 - (elapsed_seconds * 10))
"""

import unittest
import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from scoring_engine import ScoringEngine


class TestScoringEngine(unittest.TestCase):
    def test_deterministic_scoring_formula(self):
        self.assertEqual(ScoringEngine.compute_formula(30, solved=True), 9700)
        self.assertEqual(ScoringEngine.compute_formula(60, solved=True), 9400)
        self.assertEqual(ScoringEngine.compute_formula(120, solved=True), 8800)
        self.assertEqual(ScoringEngine.compute_formula(300, solved=True), 7000)
        self.assertEqual(ScoringEngine.compute_formula(600, solved=True), 4000)
        self.assertEqual(ScoringEngine.compute_formula(1000, solved=True), 0)
        self.assertEqual(ScoringEngine.compute_formula(1200, solved=True), 0)

    def test_unsolved_game_scores_zero(self):
        self.assertEqual(ScoringEngine.compute_formula(45, solved=False), 0)

    def test_calculate_game_score_payload(self):
        res = ScoringEngine.calculate_game_score(
            game_id="sudoku",
            solved=True,
            time_seconds=50,
            mistakes=1,
            difficulty="medium"
        )
        self.assertEqual(res["score"], 9500)
        self.assertEqual(res["solved"], True)
        self.assertEqual(res["time_seconds"], 50)
        self.assertEqual(res["telemetry"]["mistakes"], 1)


if __name__ == "__main__":
    unittest.main()

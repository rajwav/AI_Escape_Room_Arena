"""
Unit Tests for Quantum Minesweeper Logic Engine.
Tests:
- 9x9 Grid layout and exactly 10 mines (71 safe cells)
- 8-neighbor adjacent mine calculation
- Flag toggle logic
- 1-Life rule: mine click = instant failure
- Flood fill BFS on 0-neighbor cells
- Guaranteed single initial hint behavior
- Non-cheating Propositional CSP step deduction
- Victory state on 71 safe cell reveals
- Scoring engine integration
"""

import unittest
import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from minesweeper_engine import MinesweeperEngine
from scoring_engine import ScoringEngine


class TestMinesweeperEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MinesweeperEngine(seed=42)

    def test_grid_initialization(self):
        self.assertEqual(self.engine.ROWS, 9)
        self.assertEqual(self.engine.COLS, 9)
        self.assertEqual(len(self.engine.mines), 10)
        self.assertEqual(self.engine.TOTAL_SAFE_CELLS, 71)
        self.assertFalse(self.engine.is_game_over)
        self.assertFalse(self.engine.is_won)

    def test_initial_hint_is_safe(self):
        hint = self.engine.initial_hint
        self.assertIsNotNone(hint)
        self.assertNotIn(hint, self.engine.mines)
        hint_str = self.engine.get_initial_hint_str()
        self.assertIn("100% safe", hint_str)

    def test_flag_toggle(self):
        res1 = self.engine.toggle_flag(0, 0)
        self.assertEqual(res1["status"], "flagged")
        self.assertIn((0, 0), self.engine.flagged)

        res2 = self.engine.toggle_flag(0, 0)
        self.assertEqual(res2["status"], "unflagged")
        self.assertNotIn((0, 0), self.engine.flagged)

    def test_flagged_cell_cannot_be_revealed(self):
        self.engine.toggle_flag(1, 1)
        res = self.engine.reveal_cell(1, 1)
        self.assertEqual(res["status"], "ignored")
        self.assertNotIn((1, 1), self.engine.revealed)

    def test_single_life_mine_trigger(self):
        mine_pos = list(self.engine.mines)[0]
        res = self.engine.reveal_cell(mine_pos[0], mine_pos[1])
        self.assertEqual(res["status"], "mine_triggered")
        self.assertTrue(self.engine.is_game_over)
        self.assertFalse(self.engine.is_won)
        self.assertEqual(self.engine.triggered_mine, mine_pos)

        score_res = ScoringEngine.calculate_game_score(
            game_id="minesweeper",
            solved=False,
            time_seconds=25
        )
        self.assertEqual(score_res["score"], 0)

    def test_safe_reveal_and_initial_hint_consumed(self):
        hint = self.engine.initial_hint
        self.assertFalse(self.engine.initial_hint_consumed)
        
        res = self.engine.reveal_cell(hint[0], hint[1])
        self.assertIn(res["status"], ["revealed", "victory"])
        self.assertTrue(self.engine.initial_hint_consumed)
        self.assertIn(hint, self.engine.revealed)

    def test_adjacent_mine_count_accuracy(self):
        for r in range(9):
            for c in range(9):
                count = self.engine.get_adjacent_mines_count(r, c)
                actual_mines = sum(
                    1 for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr != 0 or dc != 0) and (r + dr, c + dc) in self.engine.mines
                )
                self.assertEqual(count, actual_mines)

    def test_ai_reasoning_step_non_cheating(self):
        # Step 1 on fresh board
        step1 = self.engine.compute_next_ai_reasoning_step()
        self.assertIsNotNone(step1)
        self.assertEqual(step1["action"], "reveal")
        self.assertIn("target_cell", step1)
        
        # Execute step 1
        self.engine.reveal_cell(*step1["target_cell"])
        self.assertGreater(len(self.engine.revealed), 0)

        # Step 2
        step2 = self.engine.compute_next_ai_reasoning_step()
        if not self.engine.is_won and not self.engine.is_game_over:
            self.assertIsNotNone(step2)
            self.assertIn(step2["action"], ["reveal", "flag"])

    def test_victory_condition(self):
        safe_cells = [
            (r, c) for r in range(9) for c in range(9)
            if (r, c) not in self.engine.mines
        ]
        for r, c in safe_cells:
            if not self.engine.is_won:
                self.engine.reveal_cell(r, c)

        self.assertTrue(self.engine.is_won)
        self.assertFalse(self.engine.is_game_over)

        score_res = ScoringEngine.calculate_game_score(
            game_id="minesweeper",
            solved=True,
            time_seconds=60
        )
        self.assertEqual(score_res["score"], 9400)


if __name__ == "__main__":
    unittest.main()

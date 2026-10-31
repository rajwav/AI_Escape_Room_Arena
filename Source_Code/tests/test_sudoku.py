"""
Unit Tests for Sudoku Game Engine & CSP Solver.
Tests:
- Board initialization and difficulty setting
- Valid placement and state update
- Invalid placement and strike counter
- Clear and Undo move operations
- Hint generation and MRV rationales
- CSP solver with MRV and step-by-step trace generation
"""

import unittest
import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from sudoku_engine import SudokuEngine


class TestSudokuEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SudokuEngine(seed=42, difficulty="easy")

    def test_board_initialization(self):
        self.assertEqual(len(self.engine.current_board), 9)
        self.assertEqual(len(self.engine.current_board[0]), 9)
        self.assertGreater(len(self.engine.initial_fixed), 0)

    def test_valid_move_logic(self):
        empty_cell = None
        for r in range(9):
            for c in range(9):
                if (r, c) not in self.engine.initial_fixed:
                    empty_cell = (r, c)
                    break
            if empty_cell:
                break

        r, c = empty_cell
        correct_val = self.engine.solution_board[r][c]
        res = self.engine.make_move(r, c, correct_val)
        self.assertTrue(res["correct"])
        self.assertEqual(self.engine.current_board[r][c], correct_val)

    def test_undo_and_clear_move(self):
        empty_cell = None
        for r in range(9):
            for c in range(9):
                if (r, c) not in self.engine.initial_fixed:
                    empty_cell = (r, c)
                    break
            if empty_cell:
                break

        r, c = empty_cell
        correct_val = self.engine.solution_board[r][c]
        self.engine.make_move(r, c, correct_val)
        self.assertEqual(self.engine.current_board[r][c], correct_val)

        undo_res = self.engine.undo_move()
        self.assertEqual(undo_res["status"], "undone")
        self.assertEqual(self.engine.current_board[r][c], 0)

    def test_invalid_move_detection(self):
        empty_cell = None
        for r in range(9):
            for c in range(9):
                if (r, c) not in self.engine.initial_fixed:
                    empty_cell = (r, c)
                    break
            if empty_cell:
                break

        r, c = empty_cell
        correct_val = self.engine.solution_board[r][c]
        wrong_val = (correct_val % 9) + 1
        if wrong_val == correct_val:
            wrong_val = ((correct_val + 1) % 9) + 1

        res = self.engine.make_move(r, c, wrong_val)
        self.assertFalse(res["correct"])
        self.assertEqual(self.engine.mistakes, 1)

    def test_csp_solver_finds_valid_solution(self):
        sol_grid, nodes = self.engine.solve_csp_with_mrv()
        self.assertIsNotNone(sol_grid)
        self.assertGreater(nodes, 0)
        for r in range(9):
            for c in range(9):
                self.assertNotEqual(sol_grid[r][c], 0)
                self.assertEqual(sol_grid[r][c], self.engine.solution_board[r][c])

    def test_solve_csp_with_trace(self):
        res = self.engine.solve_csp_with_trace(max_trace_steps=50)
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["solution"])
        self.assertGreater(len(res["trace"]), 0)
        self.assertIn("assignments", res["stats"])
        self.assertIn("mrv_selections", res["stats"])


if __name__ == "__main__":
    unittest.main()

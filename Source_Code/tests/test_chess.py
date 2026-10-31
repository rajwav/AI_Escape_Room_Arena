"""
Unit Tests for Chess Game Engine & Adversarial Search.
Tests:
- 8x8 Board initialization and piece placement
- Legal movement generation (pawns, knights, rays, kings)
- Turn switching and move execution
- Captures and piece removal
- King check detection
- Adversarial AI search evaluation, legal move execution, and turn return
"""

import unittest
import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from chess_engine import ChessEngine


class TestChessEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ChessEngine()
        self.engine.reset(mode="2p")

    def test_board_initialization(self):
        self.assertEqual(len(self.engine.board), 8)
        self.assertEqual(len(self.engine.board[0]), 8)
        self.assertEqual(self.engine.current_turn, "white")
        self.assertEqual(self.engine.board[6][0], "P")
        self.assertEqual(self.engine.board[1][0], "p")

    def test_legal_pawn_moves(self):
        legal = self.engine.get_legal_moves(6, 4)
        self.assertIn((5, 4), legal)  # 1 step
        self.assertIn((4, 4), legal)  # 2 steps

    def test_turn_switching_and_move_execution(self):
        res = self.engine.make_move(6, 4, 4, 4)
        self.assertEqual(res["status"], "moved")
        self.assertEqual(self.engine.current_turn, "black")
        self.assertEqual(self.engine.board[4][4], "P")
        self.assertEqual(self.engine.board[6][4], ".")

    def test_illegal_move_rejected(self):
        res = self.engine.make_move(6, 4, 3, 4)  # 3 steps is illegal
        self.assertEqual(res["status"], "illegal_move")

    def test_capture_piece(self):
        self.engine.board[4][4] = "P"
        self.engine.board[3][5] = "p"
        legal = self.engine.get_legal_moves(4, 4)
        self.assertIn((3, 5), legal)

        res = self.engine.make_move(4, 4, 3, 5)
        self.assertEqual(res["status"], "moved")
        self.assertIn("p", self.engine.captured_black)

    def test_check_detection(self):
        self.engine.board = [["."]*8 for _ in range(8)]
        self.engine.board[7][4] = "K"
        self.engine.board[2][4] = "r"
        self.assertTrue(self.engine.is_in_check("white"))
        self.assertFalse(self.engine.is_in_check("black"))

    def test_ai_search_evaluation_and_turn_cycle(self):
        self.engine.reset(mode="ai")
        # White moves e2 -> e4
        res_w = self.engine.make_move(6, 4, 4, 4)
        self.assertEqual(res_w["status"], "moved")
        self.assertEqual(self.engine.current_turn, "black")

        # Execute AI move
        ai_res = self.engine.evaluate_and_execute_ai_move()
        self.assertIn(ai_res["status"], ["moved", "checkmate"])
        self.assertIsNotNone(self.engine.last_ai_eval)
        self.assertGreater(self.engine.last_ai_eval["total_moves_evaluated"], 0)
        self.assertIn("search_depth", self.engine.last_ai_eval)
        self.assertIn("rationale", self.engine.last_ai_eval)

        # Turn must have returned to White
        self.assertEqual(self.engine.current_turn, "white")


if __name__ == "__main__":
    unittest.main()

"""
Unit Tests for Tic Tac Toe Engine & Minimax Game Search.
Tests:
- 3x3 Board initialization
- Move validation and turn switching
- Win and Draw detection
- Minimax blocking/winning move selection
- Minimax search telemetry and candidate branch evaluation
"""

import unittest
import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ttt_engine import TicTacToeEngine


class TestTicTacToeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TicTacToeEngine()
        self.engine.reset(mode="2p")

    def test_initial_board(self):
        self.assertEqual(len(self.engine.board), 9)
        self.assertEqual(self.engine.current_player, "X")
        self.assertFalse(self.engine.is_game_over)

    def test_valid_move_and_turn_switch(self):
        res = self.engine.make_move(0)
        self.assertEqual(self.engine.board[0], "X")
        self.assertEqual(self.engine.current_player, "O")

    def test_win_detection(self):
        self.engine.board = ["X", "X", "X", "O", "O", " ", " ", " ", " "]
        self.assertEqual(self.engine.check_winner(), "X")

    def test_draw_detection(self):
        self.engine.board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        self.assertIsNone(self.engine.check_winner())
        self.assertTrue(self.engine.is_board_full())

    def test_minimax_chooses_winning_or_blocking_move(self):
        self.engine.game_mode = "ai"
        self.engine.ai_player = "O"
        self.engine.board = ["X", "X", " ", "O", " ", " ", " ", " ", " "]
        best_move, score = self.engine.get_best_move_minimax()
        self.assertEqual(best_move, 2)

    def test_minimax_telemetry_generation(self):
        self.engine.game_mode = "ai"
        self.engine.ai_player = "O"
        self.engine.board = ["X", " ", " ", " ", "O", " ", " ", " ", " "]
        move, score, tel = self.engine.get_best_move_minimax_with_telemetry()
        self.assertIsNotNone(move)
        self.assertGreater(tel["total_nodes_expanded"], 0)
        self.assertGreater(len(tel["candidate_branches"]), 0)


if __name__ == "__main__":
    unittest.main()

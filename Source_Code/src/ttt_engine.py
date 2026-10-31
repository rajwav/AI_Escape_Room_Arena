"""
AI Escape Room Arena — Tic Tac Toe Engine & Minimax Game-State Search
Implements:
- 3x3 Board Representation
- Local 2-Player and Human vs AI Modes
- Minimax Algorithm with Game Tree Search and Optimal Move Selection
- Authentic Search Telemetry (Nodes expanded, candidate branch scores)
- Win/Draw State Detection
"""

from typing import List, Tuple, Dict, Optional, Any
import math


class TicTacToeEngine:
    """Tic Tac Toe board and Minimax game tree search engine."""

    POSITION_LABELS = {
        0: "Top-Left", 1: "Top-Center", 2: "Top-Right",
        3: "Mid-Left", 4: "Center",     5: "Mid-Right",
        6: "Bot-Left", 7: "Bot-Center", 8: "Bot-Right"
    }

    def __init__(self):
        self.board: List[str] = [" "] * 9
        self.current_player: str = "X"
        self.winner: Optional[str] = None
        self.is_draw: bool = False
        self.is_game_over: bool = False
        self.moves_count: int = 0
        self.game_mode: str = "ai"  # "2p" or "ai"
        self.ai_player: str = "O"
        self.last_ai_telemetry: Optional[Dict[str, Any]] = None

    def reset(self, mode: str = "ai"):
        self.board = [" "] * 9
        self.current_player = "X"
        self.winner = None
        self.is_draw = False
        self.is_game_over = False
        self.moves_count = 0
        self.game_mode = mode
        self.last_ai_telemetry = None

    def get_available_moves(self, board: Optional[List[str]] = None) -> List[int]:
        b = board if board is not None else self.board
        return [i for i, cell in enumerate(b) if cell == " "]

    def check_winner(self, board: Optional[List[str]] = None) -> Optional[str]:
        b = board if board is not None else self.board
        winning_lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)              # Diagonals
        ]
        for p1, p2, p3 in winning_lines:
            if b[p1] != " " and b[p1] == b[p2] == b[p3]:
                return b[p1]
        return None

    def is_board_full(self, board: Optional[List[str]] = None) -> bool:
        b = board if board is not None else self.board
        return " " not in b

    def make_move(self, index: int) -> Dict[str, Any]:
        """Executes a move at index (0-8)."""
        if self.is_game_over or self.board[index] != " ":
            return {"status": "invalid"}

        self.board[index] = self.current_player
        self.moves_count += 1

        w = self.check_winner()
        if w is not None:
            self.winner = w
            self.is_game_over = True
            return {"status": "win", "winner": w}

        if self.is_board_full():
            self.is_draw = True
            self.is_game_over = True
            return {"status": "draw"}

        # Switch Player
        self.current_player = "O" if self.current_player == "X" else "X"

        # If in AI mode and it's AI turn, trigger AI move
        if self.game_mode == "ai" and self.current_player == self.ai_player and not self.is_game_over:
            ai_idx, eval_score, telemetry = self.get_best_move_minimax_with_telemetry()
            self.last_ai_telemetry = telemetry
            if ai_idx is not None:
                self.board[ai_idx] = self.ai_player
                self.moves_count += 1
                w_ai = self.check_winner()
                if w_ai is not None:
                    self.winner = w_ai
                    self.is_game_over = True
                    return {"status": "win", "winner": w_ai, "ai_move": ai_idx}
                if self.is_board_full():
                    self.is_draw = True
                    self.is_game_over = True
                    return {"status": "draw", "ai_move": ai_idx}
                self.current_player = "X"
                return {"status": "ai_moved", "ai_move": ai_idx}

        return {"status": "moved"}

    def get_best_move_minimax(self) -> Tuple[Optional[int], int]:
        move, score, _ = self.get_best_move_minimax_with_telemetry()
        return move, score

    def get_best_move_minimax_with_telemetry(self) -> Tuple[Optional[int], int, Dict[str, Any]]:
        """Minimax Game Tree Search with complete telemetry and branch evaluation."""
        best_val = -math.inf
        best_move = None
        nodes_evaluated = [0]
        candidate_evaluations = []

        for move in self.get_available_moves():
            self.board[move] = self.ai_player
            move_val = self._minimax(self.board, depth=0, is_maximizing=False, nodes_count=nodes_evaluated)
            self.board[move] = " "

            candidate_evaluations.append({
                "cell_index": move,
                "label": self.POSITION_LABELS.get(move, f"Cell {move}"),
                "minimax_utility": move_val
            })

            if move_val > best_val:
                best_val = move_val
                best_move = move

        candidate_evaluations.sort(key=lambda x: x["minimax_utility"], reverse=True)

        telemetry = {
            "total_nodes_expanded": nodes_evaluated[0],
            "candidate_branches": candidate_evaluations,
            "chosen_move": best_move,
            "chosen_score": int(best_val) if best_val != -math.inf else 0
        }

        return best_move, int(best_val) if best_val != -math.inf else 0, telemetry

    def _minimax(self, board: List[str], depth: int, is_maximizing: bool, nodes_count: List[int]) -> int:
        nodes_count[0] += 1
        winner = self.check_winner(board)
        if winner == self.ai_player:
            return 10 - depth
        elif winner == ("X" if self.ai_player == "O" else "O"):
            return depth - 10
        elif self.is_board_full(board):
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for move in self.get_available_moves(board):
                board[move] = self.ai_player
                eval_score = self._minimax(board, depth + 1, False, nodes_count)
                board[move] = " "
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = math.inf
            human = "X" if self.ai_player == "O" else "O"
            for move in self.get_available_moves(board):
                board[move] = human
                eval_score = self._minimax(board, depth + 1, True, nodes_count)
                board[move] = " "
                min_eval = min(min_eval, eval_score)
            return min_eval

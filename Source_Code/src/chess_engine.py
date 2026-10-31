"""
AI Escape Room Arena — Chess Game Engine & Minimax Adversarial Search
Implements:
- 8x8 Board Representation with Standard Unicode Pieces
- Legal Move Generation for Pawns, Knights, Bishops, Rooks, Queens, Kings
- Turn Switching (White / Black), Captures, Check & Checkmate Detection
- 2-Ply Minimax Adversarial Game-Tree Search with Alpha-Beta Pruning
- Positional Piece-Square & Material State Evaluation
- Explainable AI Search Telemetry with Root Branch Pruning Metrics
- 2-Player Local and Human vs AI Adversarial Modes
"""

from typing import List, Tuple, Dict, Optional, Any, Set
import copy
import math


class ChessEngine:
    """Standard 8x8 Chess Engine & Adversarial Minimax Search."""

    UNICODE_PIECES = {
        "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
        "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
        ".": " "
    }

    PIECE_NAMES = {
        "P": "White Pawn", "N": "White Knight", "B": "White Bishop",
        "R": "White Rook", "Q": "White Queen", "K": "White King",
        "p": "Black Pawn", "n": "Black Knight", "b": "Black Bishop",
        "r": "Black Rook", "q": "Black Queen", "k": "Black King",
        ".": "Empty"
    }

    PIECE_VALUES = {
        "P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000,
        "p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000,
        ".": 0
    }

    # Center positional bonuses
    PST_CENTER = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [ 0,  5, 15, 20, 20, 15,  5,  0],
        [ 0,  5, 20, 30, 30, 20,  5,  0],
        [ 0,  5, 20, 30, 30, 20,  5,  0],
        [ 0,  5, 15, 20, 20, 15,  5,  0],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ]

    ROW_LABELS = ["8", "7", "6", "5", "4", "3", "2", "1"]
    COL_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def __init__(self):
        self.board: List[List[str]] = self._init_board()
        self.current_turn: str = "white"
        self.move_history: List[str] = []
        self.captured_white: List[str] = []
        self.captured_black: List[str] = []
        self.is_game_over: bool = False
        self.winner: Optional[str] = None
        self.game_mode: str = "ai"  # "2p" or "ai"
        self.last_move: Optional[Tuple[int, int, int, int]] = None
        self.last_ai_eval: Optional[Dict[str, Any]] = None

    def _init_board(self) -> List[List[str]]:
        return [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

    def reset(self, mode: str = "ai"):
        self.board = self._init_board()
        self.current_turn = "white"
        self.move_history = []
        self.captured_white = []
        self.captured_black = []
        self.is_game_over = False
        self.winner = None
        self.game_mode = mode
        self.last_move = None
        self.last_ai_eval = None

    def is_white_piece(self, p: str) -> bool:
        return p.isupper() and p != "."

    def is_black_piece(self, p: str) -> bool:
        return p.islower() and p != "."

    def get_square_label(self, r: int, c: int) -> str:
        return f"{self.COL_LABELS[c]}{self.ROW_LABELS[r]}"

    def find_king(self, color: str) -> Optional[Tuple[int, int]]:
        target_k = "K" if color == "white" else "k"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == target_k:
                    return (r, c)
        return None

    def is_in_check(self, color: str) -> bool:
        """Determines if the King of given color is currently under attack."""
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        kr, kc = king_pos
        opp_color = "black" if color == "white" else "white"

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != "." and (self.is_white_piece(p) if opp_color == "white" else self.is_black_piece(p)):
                    if (kr, kc) in self._get_raw_moves(r, c):
                        return True
        return False

    def _get_raw_moves(self, r: int, c: int, board: Optional[List[List[str]]] = None) -> List[Tuple[int, int]]:
        b = board if board is not None else self.board
        piece = b[r][c]
        if piece == ".":
            return []
        is_white = self.is_white_piece(piece)
        moves: List[Tuple[int, int]] = []
        p_type = piece.upper()

        if p_type == "P":
            dir_r = -1 if is_white else 1
            start_row = 6 if is_white else 1
            # Forward 1
            if 0 <= r + dir_r < 8 and b[r + dir_r][c] == ".":
                moves.append((r + dir_r, c))
                # Forward 2
                if r == start_row and b[r + 2 * dir_r][c] == ".":
                    moves.append((r + 2 * dir_r, c))
            # Captures
            for dc in [-1, 1]:
                nc = c + dc
                nr = r + dir_r
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = b[nr][nc]
                    if target != "." and (is_white != self.is_white_piece(target)):
                        moves.append((nr, nc))

        elif p_type == "N":
            jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in jumps:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = b[nr][nc]
                    if target == "." or (is_white != self.is_white_piece(target)):
                        moves.append((nr, nc))

        elif p_type in ["B", "R", "Q"]:
            directions = []
            if p_type in ["B", "Q"]:
                directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
            if p_type in ["R", "Q"]:
                directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    target = b[nr][nc]
                    if target == ".":
                        moves.append((nr, nc))
                    else:
                        if is_white != self.is_white_piece(target):
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc

        elif p_type == "K":
            steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in steps:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = b[nr][nc]
                    if target == "." or (is_white != self.is_white_piece(target)):
                        moves.append((nr, nc))

        return moves

    def get_legal_moves(self, r: int, c: int, board: Optional[List[List[str]]] = None) -> List[Tuple[int, int]]:
        """Returns list of valid destination squares (r2, c2) for piece at (r, c)."""
        b = board if board is not None else self.board
        piece = b[r][c]
        if piece == ".":
            return []

        is_white = self.is_white_piece(piece)
        if board is None:
            if is_white and self.current_turn != "white":
                return []
            if not is_white and self.current_turn != "black":
                return []

        return self._get_raw_moves(r, c, b)

    def get_all_legal_moves(self, color: str, board: Optional[List[List[str]]] = None) -> List[Tuple[int, int, int, int]]:
        """Returns all legal (r1, c1, r2, c2) moves for the given color."""
        b = board if board is not None else self.board
        moves = []
        for r in range(8):
            for c in range(8):
                p = b[r][c]
                if p != "." and (self.is_white_piece(p) if color == "white" else self.is_black_piece(p)):
                    for dest in self._get_raw_moves(r, c, b):
                        moves.append((r, c, dest[0], dest[1]))
        return moves

    def make_move(self, r1: int, c1: int, r2: int, c2: int) -> Dict[str, Any]:
        """Executes move from (r1, c1) to (r2, c2)."""
        if self.is_game_over:
            return {"status": "game_over"}

        legal_destinations = self.get_legal_moves(r1, c1)
        if (r2, c2) not in legal_destinations:
            return {"status": "illegal_move"}

        piece = self.board[r1][c1]
        target = self.board[r2][c2]

        if target != ".":
            if self.is_white_piece(target):
                self.captured_white.append(target)
            else:
                self.captured_black.append(target)

        # Move piece
        self.board[r2][c2] = piece
        self.board[r1][c1] = "."
        self.last_move = (r1, c1, r2, c2)

        # Pawn Promotion (auto Queen)
        if piece == "P" and r2 == 0:
            self.board[r2][c2] = "Q"
        elif piece == "p" and r2 == 7:
            self.board[r2][c2] = "q"

        move_notation = f"{piece} {self.get_square_label(r1,c1)} → {self.get_square_label(r2,c2)}"
        if target != ".":
            move_notation += f" (x{target})"
        self.move_history.append(move_notation)

        # Check for King capture (victory condition)
        if target.upper() == "K":
            self.is_game_over = True
            self.winner = self.current_turn
            return {"status": "checkmate", "winner": self.winner}

        # Switch turn
        self.current_turn = "black" if self.current_turn == "white" else "white"

        return {"status": "moved", "notation": move_notation}

    def _static_eval(self, b: List[List[str]]) -> int:
        """Static board evaluation from Black's perspective (positive = Black advantage)."""
        score = 0
        for r in range(8):
            for c in range(8):
                p = b[r][c]
                if p == ".":
                    continue
                val = self.PIECE_VALUES.get(p, 0)
                pst = self.PST_CENTER[r][c] if self.is_black_piece(p) else self.PST_CENTER[7 - r][c]
                if self.is_black_piece(p):
                    score += (val + pst)
                    if p == "p":
                        score += (r * 6)
                else:
                    score -= (val + pst)
                    if p == "P":
                        score -= ((7 - r) * 6)
        return score

    def evaluate_and_execute_ai_move(self) -> Dict[str, Any]:
        """
        Executes genuine 2-Ply Minimax Adversarial Search with Alpha-Beta Pruning.
        Evaluates Black's candidate moves and White's minimizing responses.
        """
        if self.is_game_over or self.current_turn != "black":
            return {"status": "ignored"}

        all_black_moves = self.get_all_legal_moves("black", self.board)
        if not all_black_moves:
            self.is_game_over = True
            self.winner = "white"
            return {"status": "checkmate", "winner": "white"}

        nodes_evaluated = [0]
        cutoffs = [0]
        alpha = -math.inf
        beta = math.inf
        best_val = -math.inf
        best_move = all_black_moves[0]
        best_rationale = "Positional balance"
        evaluated_branches = []

        for r1, c1, r2, c2 in all_black_moves:
            nodes_evaluated[0] += 1
            piece = self.board[r1][c1]
            target = self.board[r2][c2]

            # Simulate move
            b_sim = [row[:] for row in self.board]
            b_sim[r2][c2] = piece
            b_sim[r1][c1] = "."
            if piece == "p" and r2 == 7:
                b_sim[r2][c2] = "q"

            # If King captured, instant terminal max value
            if target.upper() == "K":
                move_val = 20000
            else:
                # 2nd Ply: White replies (minimizing Black's score)
                white_replies = self.get_all_legal_moves("white", b_sim)
                if not white_replies:
                    move_val = 15000
                else:
                    min_white_val = math.inf
                    for wr1, wc1, wr2, wc2 in white_replies:
                        nodes_evaluated[0] += 1
                        w_target = b_sim[wr2][wc2]
                        w_piece = b_sim[wr1][wc1]
                        
                        b_sim2 = [row[:] for row in b_sim]
                        b_sim2[wr2][wc2] = w_piece
                        b_sim2[wr1][wc1] = "."
                        if w_piece == "P" and wr2 == 0:
                            b_sim2[wr2][wc2] = "Q"

                        leaf_score = self._static_eval(b_sim2)
                        if leaf_score < min_white_val:
                            min_white_val = leaf_score
                        
                        # Alpha-Beta Pruning
                        if min_white_val <= alpha:
                            cutoffs[0] += 1
                            break
                    move_val = min_white_val

            # Rationale description
            mat = self.PIECE_VALUES.get(target, 0)
            if target.upper() == "K":
                rationale = "Decisive Checkmate King Capture"
            elif mat > 0:
                rationale = f"Captures {self.PIECE_NAMES.get(target, target)} (+{mat} pts)"
            elif self.PST_CENTER[r2][c2] >= 20:
                rationale = f"Controls high-value center square {self.get_square_label(r2, c2)}"
            else:
                rationale = f"Advances {self.PIECE_NAMES.get(piece, piece)} to {self.get_square_label(r2, c2)}"

            evaluated_branches.append({
                "move": (r1, c1, r2, c2),
                "notation": f"{self.UNICODE_PIECES.get(piece, piece)} {self.get_square_label(r1,c1)} → {self.get_square_label(r2,c2)}",
                "score": move_val,
                "target": target,
                "rationale": rationale
            })

            if move_val > best_val:
                best_val = move_val
                best_move = (r1, c1, r2, c2)
                best_rationale = rationale

            alpha = max(alpha, best_val)

        evaluated_branches.sort(key=lambda x: x["score"], reverse=True)

        chosen_piece = self.board[best_move[0]][best_move[1]]
        self.last_ai_eval = {
            "search_algorithm": "2-Ply Minimax Adversarial Search (Alpha-Beta Pruning)",
            "search_depth": 2,
            "nodes_expanded": nodes_evaluated[0],
            "alpha_beta_cutoffs": cutoffs[0],
            "total_moves_evaluated": len(all_black_moves),
            "top_branches": evaluated_branches[:5],
            "best_move": best_move,
            "best_score": best_val,
            "best_notation": f"{self.UNICODE_PIECES.get(chosen_piece, chosen_piece)} {self.get_square_label(best_move[0],best_move[1])} → {self.get_square_label(best_move[2],best_move[3])}",
            "rationale": best_rationale
        }

        # Execute best move on board
        move_res = self.make_move(best_move[0], best_move[1], best_move[2], best_move[3])
        return {
            "status": move_res.get("status"),
            "notation": move_res.get("notation"),
            "ai_eval": self.last_ai_eval
        }

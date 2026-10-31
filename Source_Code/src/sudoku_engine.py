"""
AI Escape Room Arena — 9x9 Sudoku Game & CSP Backtracking Solver Engine
Implements:
- 9x9 Board Representation & State Management
- Constraint Satisfaction (Rows, Columns, 3x3 Blocks, Unique Numbers)
- Backtracking Solver with Minimum Remaining Values (MRV) heuristic
- Candidate elimination and hint generator
- Procedural puzzle generator with difficulty tiers (Easy, Medium, Hard)
"""

from typing import List, Tuple, Dict, Set, Optional, Any
import random
import copy


class SudokuEngine:
    """9x9 Sudoku Board & CSP Solver Engine."""

    def __init__(self, seed: Optional[int] = None, difficulty: str = "medium"):
        self.size = 9
        self.box_size = 3
        self.seed = seed if seed is not None else random.randint(100000, 999999)
        self.difficulty = difficulty.lower()

        self.solution_board: List[List[int]] = [[0]*9 for _ in range(9)]
        self.initial_board: List[List[int]] = [[0]*9 for _ in range(9)]
        self.current_board: List[List[int]] = [[0]*9 for _ in range(9)]
        self.initial_fixed: Set[Tuple[int, int]] = set()

        self.mistakes = 0
        self.max_mistakes = 3
        self.is_game_over = False
        self.is_completed = False

        self.move_history: List[Tuple[int, int, int, int]] = []  # (r, c, prev_val, new_val)
        self.generate_new_puzzle(self.seed, self.difficulty)

    def generate_new_puzzle(self, seed: int, difficulty: str = "medium"):
        self.seed = seed
        self.difficulty = difficulty.lower()
        self.mistakes = 0
        self.is_game_over = False
        self.is_completed = False
        self.move_history.clear()

        rng = random.Random(seed)

        # 1. Generate full solved 9x9 board
        self.solution_board = [[0]*9 for _ in range(9)]
        self._fill_board_random(self.solution_board, rng)

        # 2. Number of clues based on difficulty
        clue_counts = {"easy": 40, "medium": 32, "hard": 26}
        target_clues = clue_counts.get(self.difficulty, 32)
        cells_to_remove = 81 - target_clues

        # 3. Dig cells while preserving uniqueness
        puzzle_grid = [row[:] for row in self.solution_board]
        all_positions = [(r, c) for r in range(9) for c in range(9)]
        rng.shuffle(all_positions)

        removed = 0
        for r, c in all_positions:
            if removed >= cells_to_remove:
                break
            temp = puzzle_grid[r][c]
            puzzle_grid[r][c] = 0

            # Verify uniqueness
            if self._count_solutions(puzzle_grid) != 1:
                puzzle_grid[r][c] = temp
            else:
                removed += 1

        self.initial_board = [row[:] for row in puzzle_grid]
        self.current_board = [row[:] for row in puzzle_grid]
        self.initial_fixed = {(r, c) for r in range(9) for c in range(9) if puzzle_grid[r][c] != 0}

    def _fill_board_random(self, board: List[List[int]], rng: random.Random) -> bool:
        empty = self._find_empty(board)
        if not empty:
            return True
        r, c = empty
        nums = list(range(1, 10))
        rng.shuffle(nums)
        for num in nums:
            if self.is_valid_move(board, r, c, num):
                board[r][c] = num
                if self._fill_board_random(board, rng):
                    return True
                board[r][c] = 0
        return False

    def _count_solutions(self, board: List[List[int]], limit: int = 2) -> int:
        count = [0]
        def solve_count(b):
            if count[0] >= limit:
                return
            empty = self._find_empty(b)
            if not empty:
                count[0] += 1
                return
            r, c = empty
            for num in range(1, 10):
                if self.is_valid_move(b, r, c, num):
                    b[r][c] = num
                    solve_count(b)
                    b[r][c] = 0
        b_copy = [row[:] for row in board]
        solve_count(b_copy)
        return count[0]

    def _find_empty(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return (r, c)
        return None

    def is_valid_move(self, board: List[List[int]], r: int, c: int, num: int) -> bool:
        # Row check
        for j in range(9):
            if j != c and board[r][j] == num:
                return False
        # Column check
        for i in range(9):
            if i != r and board[i][c] == num:
                return False
        # 3x3 Box check
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i != r or j != c) and board[i][j] == num:
                    return False
        return True

    def get_candidates(self, board: List[List[int]], r: int, c: int) -> List[int]:
        if board[r][c] != 0:
            return []
        return [num for num in range(1, 10) if self.is_valid_move(board, r, c, num)]

    def get_completed_numbers(self) -> Set[int]:
        """Returns set of numbers (1-9) that are completely placed on the board (count >= 9)."""
        counts: Dict[int, int] = {d: 0 for d in range(1, 10)}
        for r in range(9):
            for c in range(9):
                val = self.current_board[r][c]
                if val in counts:
                    counts[val] += 1
        return {d for d, count in counts.items() if count >= 9}

    def make_move(self, r: int, c: int, num: int) -> Dict[str, Any]:
        """Player makes a move."""
        if (r, c) in self.initial_fixed or self.is_game_over or self.is_completed:
            return {"status": "ignored"}

        prev_val = self.current_board[r][c]
        if num == 0:
            self.current_board[r][c] = 0
            if prev_val != 0:
                self.move_history.append((r, c, prev_val, 0))
            return {"status": "cleared"}

        # Validate against true solution
        if self.solution_board[r][c] == num:
            self.current_board[r][c] = num
            self.move_history.append((r, c, prev_val, num))
            if self._find_empty(self.current_board) is None:
                self.is_completed = True
                return {"status": "completed", "correct": True}
            return {"status": "valid", "correct": True}
        else:
            self.mistakes += 1
            if self.mistakes >= self.max_mistakes:
                self.is_game_over = True
                return {"status": "game_over", "correct": False}
            return {"status": "mistake", "correct": False, "mistakes": self.mistakes}

    def undo_move(self) -> Dict[str, Any]:
        """Undoes the last player move."""
        if not self.move_history:
            return {"status": "no_history"}
        r, c, prev_val, _ = self.move_history.pop()
        self.current_board[r][c] = prev_val
        self.is_completed = False
        self.is_game_over = False
        return {"status": "undone", "cell": (r, c), "value": prev_val}

    def solve_csp_with_mrv(self) -> Tuple[Optional[List[List[int]]], int]:
        """
        Backtracking CSP Solver using Minimum Remaining Values (MRV) heuristic.
        Returns (solution_grid, nodes_expanded).
        """
        board_copy = [row[:] for row in self.current_board]
        nodes_expanded = [0]

        def backtrack(b: List[List[int]]) -> bool:
            nodes_expanded[0] += 1
            # Select unassigned variable with MRV
            min_candidates = 10
            best_cell = None
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        cands = self.get_candidates(b, r, c)
                        if len(cands) < min_candidates:
                            min_candidates = len(cands)
                            best_cell = (r, c, cands)
                            if min_candidates == 0:
                                return False  # Dead end

            if best_cell is None:
                return True  # All assigned!

            r, c, candidates = best_cell
            for val in candidates:
                b[r][c] = val
                if backtrack(b):
                    return True
                b[r][c] = 0
            return False

        success = backtrack(board_copy)
        return (board_copy if success else None, nodes_expanded[0])

    def solve_csp_with_trace(self, max_trace_steps: int = 150) -> Dict[str, Any]:
        """
        Executes CSP Backtracking + MRV and records a step-by-step reasoning trace.
        Returns solution grid, trace log events, and authentic solver telemetry.
        """
        import time
        start_t = time.perf_counter()
        board_copy = [row[:] for row in self.current_board]
        trace: List[Dict[str, Any]] = []
        stats = {
            "nodes_expanded": 0,
            "assignments": 0,
            "backtracks": 0,
            "mrv_selections": 0,
            "elapsed_ms": 0.0
        }

        def backtrack(b: List[List[int]]) -> bool:
            stats["nodes_expanded"] += 1
            # Select unassigned variable with MRV
            min_candidates = 10
            best_cell = None
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        cands = self.get_candidates(b, r, c)
                        if len(cands) < min_candidates:
                            min_candidates = len(cands)
                            best_cell = (r, c, cands)
                            if min_candidates == 0:
                                return False

            if best_cell is None:
                return True

            r, c, candidates = best_cell
            stats["mrv_selections"] += 1

            if len(trace) < max_trace_steps:
                trace.append({
                    "action": "mrv_select",
                    "cell": (r, c),
                    "candidates": candidates,
                    "board_snapshot": [row[:] for row in b],
                    "desc": f"MRV selected R{r+1}C{c+1} with domain {candidates}"
                })

            for val in candidates:
                stats["assignments"] += 1
                b[r][c] = val
                if len(trace) < max_trace_steps:
                    trace.append({
                        "action": "try_value",
                        "cell": (r, c),
                        "val": val,
                        "board_snapshot": [row[:] for row in b],
                        "desc": f"Assigned {val} to R{r+1}C{c+1} → Constraint check: PASS"
                    })

                if backtrack(b):
                    return True

                stats["backtracks"] += 1
                b[r][c] = 0
                if len(trace) < max_trace_steps:
                    trace.append({
                        "action": "backtrack",
                        "cell": (r, c),
                        "val": val,
                        "board_snapshot": [row[:] for row in b],
                        "desc": f"Backtracking on R{r+1}C{c+1} (removed {val})"
                    })

            return False

        success = backtrack(board_copy)
        stats["elapsed_ms"] = round((time.perf_counter() - start_t) * 1000, 2)

        return {
            "success": success,
            "solution": board_copy if success else None,
            "trace": trace,
            "stats": stats
        }

    def get_hint(self) -> Optional[Dict[str, Any]]:
        """Provides a single cell hint with candidate rationale."""
        for r in range(9):
            for c in range(9):
                if self.current_board[r][c] == 0:
                    cands = self.get_candidates(self.current_board, r, c)
                    correct_val = self.solution_board[r][c]
                    return {
                        "row": r,
                        "col": c,
                        "correct_value": correct_val,
                        "candidates": cands,
                        "rationale": f"Cell R{r+1}C{c+1} valid candidates are {cands}. Unique assignment is {correct_val}."
                    }
        return None

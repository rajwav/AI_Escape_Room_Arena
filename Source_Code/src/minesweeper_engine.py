"""
AI Escape Room Arena — Quantum Minesweeper Engine (Logic & Deduction)
Implements:
- 9x9 Grid with exactly 10 hidden mines (71 safe cells)
- Adjacent mine calculation over 8 neighboring cells
- Flood-fill BFS reveal on 0-neighbor cells
- Flagging / Unflagging system
- 1 Life Survival System (Mine click = instant Game Over)
- Guaranteed Initial AI Hint (Single safe cell revealed at start, no further hints allowed)
- Strict Non-Cheating Propositional Logic & CSP Step-by-Step Solver
  (AI reads only from visible_numbers, flags, and revealed sets — never inspecting hidden mine set)
- Deterministic Time-Based Scoring Integration
"""

from typing import List, Tuple, Dict, Set, Optional, Any
from collections import deque
import random


class MinesweeperEngine:
    """9x9 Minesweeper Logic & Deduction Engine."""

    ROWS = 9
    COLS = 9
    NUM_MINES = 10
    TOTAL_SAFE_CELLS = 71  # 81 - 10

    ROW_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(100000, 999999)
        self.mines: Set[Tuple[int, int]] = set()
        self.revealed: Set[Tuple[int, int]] = set()
        self.flagged: Set[Tuple[int, int]] = set()
        # Visible clue numbers available only upon cell reveal
        self.visible_numbers: Dict[Tuple[int, int], int] = {}
        
        self.is_game_over: bool = False
        self.is_won: bool = False
        self.triggered_mine: Optional[Tuple[int, int]] = None
        self.initial_hint: Optional[Tuple[int, int]] = None
        self.initial_hint_consumed: bool = False
        self.moves_count: int = 0

        self.reset_game(self.seed)

    def reset_game(self, seed: Optional[int] = None):
        if seed is not None:
            self.seed = seed
        self.mines.clear()
        self.revealed.clear()
        self.flagged.clear()
        self.visible_numbers.clear()
        self.is_game_over = False
        self.is_won = False
        self.triggered_mine = None
        self.initial_hint_consumed = False
        self.moves_count = 0

        rng = random.Random(self.seed)
        all_cells = [(r, c) for r in range(self.ROWS) for c in range(self.COLS)]
        rng.shuffle(all_cells)

        # Place exactly 10 mines
        self.mines = set(all_cells[:self.NUM_MINES])

        # Precompute initial safe starting hint
        safe_candidates = [
            (r, c) for (r, c) in all_cells[self.NUM_MINES:]
            if self._compute_adjacent_mines(r, c) == 0
        ]
        if not safe_candidates:
            safe_candidates = list(set(all_cells) - self.mines)

        self.initial_hint = rng.choice(safe_candidates) if safe_candidates else (4, 4)

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Returns 8 adjacent grid coordinates."""
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                    neighbors.append((nr, nc))
        return neighbors

    def _compute_adjacent_mines(self, r: int, c: int) -> int:
        """Internal board evaluation: counts mines in 8 neighbors."""
        count = 0
        for nr, nc in self.get_neighbors(r, c):
            if (nr, nc) in self.mines:
                count += 1
        return count

    def get_adjacent_mines_count(self, r: int, c: int) -> int:
        """Returns the adjacent mine count for a cell."""
        if (r, c) in self.visible_numbers:
            return self.visible_numbers[(r, c)]
        # For game mechanics / UI rendering of revealed cells
        return self._compute_adjacent_mines(r, c)

    def get_cell_label(self, r: int, c: int) -> str:
        return f"{self.ROW_LABELS[r]}{c + 1}"

    def get_initial_hint_str(self) -> str:
        """Returns the single guaranteed safe starting move."""
        if self.initial_hint is not None:
            r, c = self.initial_hint
            return f"Cell {self.get_cell_label(r, c)} ({self.ROW_LABELS[r]}, Col {c+1}) is 100% safe."
        return "Cell E5 is guaranteed safe."

    def toggle_flag(self, r: int, c: int) -> Dict[str, Any]:
        """Toggles flag on a non-revealed cell."""
        if self.is_game_over or self.is_won or (r, c) in self.revealed:
            return {"status": "ignored"}

        if (r, c) in self.flagged:
            self.flagged.remove((r, c))
            return {"status": "unflagged", "cell": (r, c)}
        else:
            self.flagged.add((r, c))
            return {"status": "flagged", "cell": (r, c)}

    def reveal_cell(self, r: int, c: int) -> Dict[str, Any]:
        """Reveals a cell. Flagged cells cannot be revealed."""
        if self.is_game_over or self.is_won:
            return {"status": "game_over"}

        if (r, c) in self.flagged or (r, c) in self.revealed:
            return {"status": "ignored"}

        self.moves_count += 1
        self.initial_hint_consumed = True

        # Check if mine hit
        if (r, c) in self.mines:
            self.revealed.add((r, c))
            self.triggered_mine = (r, c)
            self.is_game_over = True
            return {"status": "mine_triggered", "cell": (r, c), "won": False}

        # Safe cell - Flood fill if adjacent count is 0
        queue = deque([(r, c)])
        self.revealed.add((r, c))
        self.visible_numbers[(r, c)] = self._compute_adjacent_mines(r, c)

        while queue:
            curr_r, curr_c = queue.popleft()
            adj_count = self.visible_numbers.get((curr_r, curr_c), self._compute_adjacent_mines(curr_r, curr_c))
            self.visible_numbers[(curr_r, curr_c)] = adj_count

            if adj_count == 0:
                for nr, nc in self.get_neighbors(curr_r, curr_c):
                    if (nr, nc) not in self.revealed and (nr, nc) not in self.flagged and (nr, nc) not in self.mines:
                        self.revealed.add((nr, nc))
                        neighbor_adj = self._compute_adjacent_mines(nr, nc)
                        self.visible_numbers[(nr, nc)] = neighbor_adj
                        if neighbor_adj == 0:
                            queue.append((nr, nc))

        # Check win condition (all safe cells revealed)
        safe_revealed_count = len(self.revealed - self.mines)
        if safe_revealed_count >= self.TOTAL_SAFE_CELLS:
            self.is_won = True
            return {"status": "victory", "won": True}

        return {"status": "revealed", "cell": (r, c), "safe_count": safe_revealed_count}

    def compute_next_ai_reasoning_step(self) -> Optional[Dict[str, Any]]:
        """
        Strictly Non-Cheating Propositional Logic & CSP Deduction Step.
        The AI reads ONLY from:
        - self.visible_numbers (clues revealed on the board)
        - self.revealed (set of revealed coordinates)
        - self.flagged (set of flagged coordinates)
        It NEVER accesses self.mines to make decisions.
        """
        if self.is_game_over or self.is_won:
            return None

        # 1. Starting move if board is completely unrevealed
        if not self.revealed:
            start_cell = self.initial_hint if self.initial_hint else (4, 4)
            return {
                "analyzed_cell": start_cell,
                "adjacent_k": 0,
                "neighbors": self.get_neighbors(*start_cell),
                "known_mines": [],
                "unknowns": [start_cell],
                "deduction_rule": "Initial A-Priori Propositional Axiom (Guaranteed Safe First Move)",
                "action": "reveal",
                "target_cell": start_cell,
                "rationale": f"Initial probe on sector {self.get_cell_label(*start_cell)} to initiate constraint propagation."
            }

        # Collect revealed frontier cells strictly from visible_numbers
        frontier_cells: List[Tuple[int, int]] = []
        for r, c in self.revealed:
            k = self.visible_numbers.get((r, c), 0)
            if k > 0:
                unrev = [n for n in self.get_neighbors(r, c) if n not in self.revealed and n not in self.flagged]
                if unrev:
                    frontier_cells.append((r, c))

        # 2. Deterministic Single-Cell Horn-Clause Unit Resolution
        for r, c in frontier_cells:
            k = self.visible_numbers.get((r, c), 0)
            neighbors = self.get_neighbors(r, c)
            flagged = [n for n in neighbors if n in self.flagged]
            unknowns = [n for n in neighbors if n not in self.revealed and n not in self.flagged]

            if not unknowns:
                continue

            # Rule 1: All remaining unknowns are mines
            if len(unknowns) + len(flagged) == k:
                target = unknowns[0]
                return {
                    "analyzed_cell": (r, c),
                    "adjacent_k": k,
                    "neighbors": neighbors,
                    "known_mines": flagged,
                    "unknowns": unknowns,
                    "deduction_rule": "Rule 1: |Unknowns| + |Known Flags| == Visible Clue ➔ Guaranteed MINE",
                    "action": "flag",
                    "target_cell": target,
                    "rationale": f"Analysing visible sector {self.get_cell_label(r,c)} (Clue={k}). Unknowns={len(unknowns)}, Flags={len(flagged)}. Sector {self.get_cell_label(*target)} is a confirmed MINE ➔ Placed Flag."
                }

            # Rule 2: All required mines are flagged ➔ All remaining unknowns are safe
            if len(flagged) == k:
                target = unknowns[0]
                return {
                    "analyzed_cell": (r, c),
                    "adjacent_k": k,
                    "neighbors": neighbors,
                    "known_mines": flagged,
                    "unknowns": unknowns,
                    "deduction_rule": "Rule 2: |Known Flags| == Visible Clue ➔ Guaranteed SAFE",
                    "action": "reveal",
                    "target_cell": target,
                    "rationale": f"Analysing visible sector {self.get_cell_label(r,c)} (Clue={k}). Flags={len(flagged)}. All {k} mines satisfied ➔ Sector {self.get_cell_label(*target)} is SAFE ➔ Revealed."
                }

        # 3. Deterministic Pairwise Subset / Overlap Deduction
        for i in range(len(frontier_cells)):
            for j in range(i + 1, len(frontier_cells)):
                rA, cA = frontier_cells[i]
                rB, cB = frontier_cells[j]

                kA = self.visible_numbers.get((rA, cA), 0)
                kB = self.visible_numbers.get((rB, cB), 0)

                fA = [n for n in self.get_neighbors(rA, cA) if n in self.flagged]
                fB = [n for n in self.get_neighbors(rB, cB) if n in self.flagged]

                uA = set([n for n in self.get_neighbors(rA, cA) if n not in self.revealed and n not in self.flagged])
                uB = set([n for n in self.get_neighbors(rB, cB) if n not in self.revealed and n not in self.flagged])

                remA = kA - len(fA)
                remB = kB - len(fB)

                if uA and uB:
                    # Subset rule: uA is subset of uB
                    if uA.issubset(uB) and uA != uB:
                        diff = uB - uA
                        if remB == remA:
                            target = list(diff)[0]
                            return {
                                "analyzed_cell": (rB, cB),
                                "adjacent_k": kB,
                                "neighbors": self.get_neighbors(rB, cB),
                                "known_mines": fB,
                                "unknowns": list(uB),
                                "deduction_rule": "Rule 3: Pairwise Subset Constraint Propagation (Set Difference is SAFE)",
                                "action": "reveal",
                                "target_cell": target,
                                "rationale": f"Subset overlap between {self.get_cell_label(rA,cA)} and {self.get_cell_label(rB,cB)}. Remaining mines equal ({remA}) ➔ Difference cell {self.get_cell_label(*target)} is SAFE."
                            }
                        elif remB - remA == len(diff):
                            target = list(diff)[0]
                            return {
                                "analyzed_cell": (rB, cB),
                                "adjacent_k": kB,
                                "neighbors": self.get_neighbors(rB, cB),
                                "known_mines": fB,
                                "unknowns": list(uB),
                                "deduction_rule": "Rule 3: Pairwise Subset Constraint Propagation (Set Difference is MINE)",
                                "action": "flag",
                                "target_cell": target,
                                "rationale": f"Subset overlap between {self.get_cell_label(rA,cA)} and {self.get_cell_label(rB,cB)}. Mine differential equals subset size ➔ Difference cell {self.get_cell_label(*target)} is a MINE."
                            }

        # 4. Probabilistic Minimum-Risk Choice (when no deterministic rule applies)
        candidate_probs = []
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if (r, c) not in self.revealed and (r, c) not in self.flagged:
                    # Compute min probability strictly from visible numbers on bordering cells
                    border_probs = []
                    for nr, nc in self.get_neighbors(r, c):
                        if (nr, nc) in self.revealed:
                            kn = self.visible_numbers.get((nr, nc), 0)
                            fn = sum(1 for n in self.get_neighbors(nr, nc) if n in self.flagged)
                            un = sum(1 for n in self.get_neighbors(nr, nc) if n not in self.revealed and n not in self.flagged)
                            if un > 0:
                                border_probs.append(max(0, (kn - fn) / un))
                    prob = min(border_probs) if border_probs else 0.12
                    candidate_probs.append(((r, c), prob))

        if candidate_probs:
            candidate_probs.sort(key=lambda x: x[1])
            best_cell, best_p = candidate_probs[0]
            return {
                "analyzed_cell": best_cell,
                "adjacent_k": 0,
                "neighbors": self.get_neighbors(*best_cell),
                "known_mines": list(self.flagged),
                "unknowns": [best_cell],
                "deduction_rule": f"Rule 4: Minimum Risk Visible Clue Heuristic (P(Mine) = {best_p:.2f})",
                "action": "reveal",
                "target_cell": best_cell,
                "rationale": f"No deterministic deductions remaining from visible clues. Probing lowest-risk frontier cell {self.get_cell_label(*best_cell)} (Estimated risk: {best_p*100:.1f}%)."
            }

        return None

    def get_reasoning_explanation(self) -> str:
        """Returns AIML Propositional Constraint Logic explanation."""
        return (
            "Minesweeper is modeled as a Propositional Constraint Satisfaction Problem (CSP). "
            "For each revealed cell $C_{i,j} = k$, let $N(C_{i,j})$ be its 8 neighbors. "
            "The exact constraint is: $\\sum_{N \\in N(C_{i,j})} \\text{Mine}(N) = k$. "
            "When the number of unrevealed neighbors equals $k$, all unrevealed neighbors are mines. "
            "When all $k$ mines are flagged, all remaining unrevealed neighbors are guaranteed safe."
        )

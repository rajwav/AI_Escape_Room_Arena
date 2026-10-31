"""
AI Escape Room - Constraint Satisfaction Problem (CSP) Puzzle Engine
Demonstrates Backtracking Search, Domain Filtering, and Constraint Propagation.
Used for combinatorial cipher locks, dial codes, and chemical synthesis puzzles.
"""

from typing import Dict, List, Callable, Any, Optional, Tuple


class CSP:
    """
    Formal Constraint Satisfaction Problem Formulation:
    Variables (X), Domains (D), Constraints (C).
    """
    def __init__(self, variables: List[str], domains: Dict[str, List[Any]]):
        self.variables = variables
        self.domains = {v: list(domains[v]) for v in variables}
        self.constraints: Dict[str, List[Tuple[Tuple[str, ...], Callable[..., bool]]]] = {
            v: [] for v in variables
        }

    def add_constraint(self, scope: Tuple[str, ...], predicate: Callable[..., bool]):
        """Adds a constraint function over a subset of variables."""
        for var in scope:
            if var in self.constraints:
                self.constraints[var].append((scope, predicate))

    def is_consistent(self, var: str, assignment: Dict[str, Any]) -> bool:
        """Checks if assigning 'var' satisfies all relevant constraints."""
        for scope, predicate in self.constraints[var]:
            # Only evaluate if all variables in scope are already assigned
            if all(v in assignment for v in scope):
                args = [assignment[v] for v in scope]
                if not predicate(*args):
                    return False
        return True

    def backtrack_search(self) -> Optional[Dict[str, Any]]:
        """Backtracking search algorithm with Forward Checking."""
        return self._backtrack({})

    def _backtrack(self, assignment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if len(assignment) == len(self.variables):
            return assignment

        # Select unassigned variable (MRV - Minimum Remaining Values heuristic)
        unassigned = [v for v in self.variables if v not in assignment]
        unassigned.sort(key=lambda var: len(self.domains[var]))
        var = unassigned[0]

        for value in self.domains[var]:
            assignment[var] = value
            if self.is_consistent(var, assignment):
                result = self._backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]

        return None


class EscapeRoomPuzzles:
    """Factory of predefined escape room constraint puzzles."""

    @staticmethod
    def solve_vault_lock(clues_unlocked: bool = True) -> Dict[str, Any]:
        """
        Vault 3-Digit Combination Lock Puzzle:
        Variables: D1, D2, D3 in {1, 2, ..., 9}
        Clues from environment:
        1. All digits are strictly distinct.
        2. Sum of digits D1 + D2 + D3 == 15
        3. D1 < D2 < D3 (strictly ascending)
        4. D2 is a prime number {2, 3, 5, 7}
        5. D3 = D1 * 2 + 1 (discovered in lab notebook)
        """
        digits = list(range(1, 10))
        csp = CSP(
            variables=["D1", "D2", "D3"],
            domains={"D1": digits, "D2": digits, "D3": digits}
        )

        # Constraint 1: All distinct
        csp.add_constraint(("D1", "D2"), lambda d1, d2: d1 != d2)
        csp.add_constraint(("D2", "D3"), lambda d2, d3: d2 != d3)
        csp.add_constraint(("D1", "D3"), lambda d1, d3: d1 != d3)

        # Constraint 2: Sum is 15
        csp.add_constraint(("D1", "D2", "D3"), lambda d1, d2, d3: d1 + d2 + d3 == 15)

        # Constraint 3: Ascending order
        csp.add_constraint(("D1", "D2"), lambda d1, d2: d1 < d2)
        csp.add_constraint(("D2", "D3"), lambda d2, d3: d2 < d3)

        # Constraint 4: D2 is prime
        primes = {2, 3, 5, 7}
        csp.add_constraint(("D2",), lambda d2: d2 in primes)

        # Constraint 5: D3 = 2*D1 + 1 (Lab Clue)
        if clues_unlocked:
            csp.add_constraint(("D1", "D3"), lambda d1, d3: d3 == (2 * d1 + 1))

        solution = csp.backtrack_search()
        return solution

    @staticmethod
    def solve_chemical_reagent_puzzle() -> Optional[Dict[str, int]]:
        """
        Chemical Synthesis Puzzle:
        Variables: Reagent_A, Reagent_B, Reagent_C (milliliters: 1 to 5)
        Constraints:
        - Total volume == 9 ml
        - Reagent_A * 2 == Reagent_B
        - Reagent_C > Reagent_A
        """
        csp = CSP(
            variables=["Reagent_A", "Reagent_B", "Reagent_C"],
            domains={
                "Reagent_A": [1, 2, 3, 4, 5],
                "Reagent_B": [1, 2, 3, 4, 5],
                "Reagent_C": [1, 2, 3, 4, 5]
            }
        )
        csp.add_constraint(("Reagent_A", "Reagent_B", "Reagent_C"), lambda a, b, c: a + b + c == 9)
        csp.add_constraint(("Reagent_A", "Reagent_B"), lambda a, b: 2 * a == b)
        csp.add_constraint(("Reagent_A", "Reagent_C"), lambda a, c: c > a)
        return csp.backtrack_search()

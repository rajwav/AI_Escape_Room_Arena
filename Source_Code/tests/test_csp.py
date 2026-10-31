"""
Unit Tests for Constraint Satisfaction Problem (CSP) Solver
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from puzzle_engine import CSP, EscapeRoomPuzzles


class TestCSPEngine(unittest.TestCase):
    def test_simple_binary_csp(self):
        csp = CSP(variables=["X", "Y"], domains={"X": [1, 2, 3], "Y": [1, 2, 3]})
        csp.add_constraint(("X", "Y"), lambda x, y: x + y == 5)
        csp.add_constraint(("X", "Y"), lambda x, y: x < y)
        
        sol = csp.backtrack_search()
        self.assertIsNotNone(sol)
        self.assertEqual(sol["X"], 2)
        self.assertEqual(sol["Y"], 3)

    def test_vault_3_digit_lock_csp(self):
        sol = EscapeRoomPuzzles.solve_vault_lock(clues_unlocked=True)
        self.assertIsNotNone(sol)
        self.assertEqual(sol["D1"] + sol["D2"] + sol["D3"], 15)
        self.assertLess(sol["D1"], sol["D2"])
        self.assertLess(sol["D2"], sol["D3"])
        self.assertEqual(sol["D3"], 2 * sol["D1"] + 1)
        self.assertIn(sol["D2"], [2, 3, 5, 7])

    def test_chemical_reagents_csp(self):
        sol = EscapeRoomPuzzles.solve_chemical_reagent_puzzle()
        self.assertIsNotNone(sol)
        self.assertEqual(sol["Reagent_A"] + sol["Reagent_B"] + sol["Reagent_C"], 9)
        self.assertEqual(2 * sol["Reagent_A"], sol["Reagent_B"])
        self.assertGreater(sol["Reagent_C"], sol["Reagent_A"])


if __name__ == "__main__":
    unittest.main()

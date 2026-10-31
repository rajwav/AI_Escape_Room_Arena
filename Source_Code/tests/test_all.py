"""
Master Test Suite Runner for Project 2: AI Escape Room & Game Arena Platform
Executes all unit and integration tests across:
1. Knowledge Representation & Inference (test_inference.py)
2. State-Space Planning & A* Search (test_search.py)
3. Constraint Satisfaction (CSP) Engine (test_csp.py)
4. ML Adaptive Difficulty & K-Means/Decision Tree (test_ml_module.py)
5. Quantum Sudoku CSP Solver (test_sudoku.py)
6. Quantum Minesweeper Logic Engine (test_minesweeper.py)
7. Tic Tac Toe Minimax Search (test_tic_tac_toe.py)
8. Quantum Chess Engine & Legal Moves (test_chess.py)
9. Centralized Deterministic Scoring Engine (test_scoring.py)
"""

import unittest
import sys
import os

test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(test_dir, "..", "src")
sys.path.insert(0, src_dir)
sys.path.insert(0, test_dir)

from test_inference import TestInferenceEngine
from test_search import TestSearchAlgorithms
from test_csp import TestCSPEngine
from test_ml_module import TestMLModule
from test_sudoku import TestSudokuEngine
from test_minesweeper import TestMinesweeperEngine
from test_tic_tac_toe import TestTicTacToeEngine
from test_chess import TestChessEngine
from test_scoring import TestScoringEngine


def run_master_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestInferenceEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchAlgorithms))
    suite.addTests(loader.loadTestsFromTestCase(TestCSPEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMLModule))
    suite.addTests(loader.loadTestsFromTestCase(TestSudokuEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMinesweeperEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestTicTacToeEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestChessEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestScoringEngine))

    print("\n" + "=" * 70)
    print("      AI GAME ARENA: EXECUTING FULL AUTOMATED TEST SUITE")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    print(f" TOTAL TESTS RUN : {result.testsRun}")
    print(f" SUCCESSES      : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" FAILURES       : {len(result.failures)}")
    print(f" ERRORS         : {len(result.errors)}")
    print("=" * 70)
    if result.wasSuccessful():
        print(">> ALL SYSTEMS NOMINAL: 100% OF TESTS PASSED SUCCESSFULLY! <<\n")
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_master_suite()
    sys.exit(0 if success else 1)

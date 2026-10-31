"""
Unit Tests for State Space and Search Algorithms (BFS & A*)
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from environment import EscapeRoomEnvironment, GameState
from search_algorithms import EscapeRoomSearchPlanner


class TestSearchAlgorithms(unittest.TestCase):
    def setUp(self):
        self.env = EscapeRoomEnvironment()
        self.planner = EscapeRoomSearchPlanner(self.env)

    def test_environment_initial_state(self):
        st = self.env.get_initial_state()
        self.assertEqual(st.current_room, "Foyer")
        self.assertFalse(self.env.is_goal_state(st))

    def test_bfs_finds_goal(self):
        res = self.planner.breadth_first_search()
        self.assertTrue(res.solution_found)
        self.assertGreater(res.path_cost, 0)
        self.assertIn("Escape_Portal", res.solution_path[-1][1].current_room)

    def test_a_star_optimality(self):
        bfs_res = self.planner.breadth_first_search()
        astar_res = self.planner.a_star_search()

        self.assertTrue(astar_res.solution_found)
        # A* and BFS must find the exact same optimal step length
        self.assertEqual(bfs_res.path_cost, astar_res.path_cost)
        # A* should explore fewer or equal nodes compared to BFS
        self.assertLessEqual(astar_res.nodes_explored, bfs_res.nodes_explored)

    def test_heuristic_admissibility_at_start(self):
        st = self.env.get_initial_state()
        h_val = self.planner.calculate_heuristic(st)
        # h(s) should be strictly positive at start and <= optimal path cost (13 steps)
        self.assertGreater(h_val, 0)
        self.assertLessEqual(h_val, 13)


if __name__ == "__main__":
    unittest.main()

"""
AI Escape Room - Intelligent Search Algorithms Module
Implements Uninformed Search (BFS) and Informed Heuristic Search (A*).
Demonstrates State Space Exploration, Admissible Heuristics, and Empirical Benchmarks.
"""

import time
import heapq
from collections import deque
from typing import List, Tuple, Dict, Set, Optional, Any
from dataclasses import dataclass
from environment import GameState, EscapeRoomEnvironment
from knowledge_base import KnowledgeBase
from inference_engine import ForwardChainingEngine, InferenceStep


@dataclass
class SearchResult:
    """Encapsulates empirical search metrics for academic evaluation."""
    algorithm_name: str
    solution_found: bool
    solution_path: List[Tuple[str, GameState]]  # [(Action, State)]
    path_cost: int
    nodes_explored: int
    max_frontier_size: int
    execution_time_ms: float

    def get_summary(self) -> Dict[str, Any]:
        return {
            "Algorithm": self.algorithm_name,
            "Success": self.solution_found,
            "Steps to Escape": self.path_cost,
            "Nodes Explored": self.nodes_explored,
            "Peak Frontier": self.max_frontier_size,
            "Time (ms)": round(self.execution_time_ms, 3)
        }


class EscapeRoomSearchPlanner:
    """
    Solves the escape room state space using Breadth-First Search (BFS) and A* Search.
    """
    def __init__(self, env: EscapeRoomEnvironment):
        self.env = env

    def breadth_first_search(self, initial_state: Optional[GameState] = None) -> SearchResult:
        """
        Uninformed Search: Breadth-First Search (BFS).
        Layer-by-layer exploration using FIFO queue.
        Guarantees shortest path in uniform-cost state space.
        """
        start_time = time.perf_counter()
        if initial_state is None:
            initial_state = self.env.get_initial_state()

        if self.env.is_goal_state(initial_state):
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return SearchResult("Breadth-First Search (BFS)", True, [("START", initial_state)], 0, 1, 1, elapsed)

        queue = deque([(initial_state, [])])  # (state, path)
        visited: Set[GameState] = {initial_state}
        nodes_explored = 0
        max_frontier = 1

        while queue:
            max_frontier = max(max_frontier, len(queue))
            current_state, path = queue.popleft()
            nodes_explored += 1

            if self.env.is_goal_state(current_state):
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return SearchResult(
                    algorithm_name="Breadth-First Search (BFS)",
                    solution_found=True,
                    solution_path=path + [("GOAL_REACHED", current_state)],
                    path_cost=len(path),
                    nodes_explored=nodes_explored,
                    max_frontier_size=max_frontier,
                    execution_time_ms=elapsed
                )

            for action, next_state, cost in self.env.get_successors(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [(action, current_state)]))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        return SearchResult("Breadth-First Search (BFS)", False, [], -1, nodes_explored, max_frontier, elapsed)

    def calculate_heuristic(self, state: GameState) -> int:
        """
        Admissible and Consistent Heuristic Function h(s):
        h(s) = room_graph_distance + count(essential_missing_milestones)

        Admissibility proof:
        - Reaching the exit chamber requires at least the Manhattan graph distance to Escape_Portal.
        - Activating the portal strictly requires at least:
            1. Synthesizing acid (if not done) -> at least 1 action
            2. Unlocking vault (if not done) -> at least 1 action
            3. Opening safe (if not done) -> at least 1 action
            4. Activating portal (if not done) -> at least 1 action
        Since these milestones cannot be bypassed, h(s) <= h*(s) for all s.
        """
        facts = set(state.world_facts)
        inv = set(state.inventory)
        room = state.current_room

        # Spatial distance to Escape_Portal
        target_coords = self.env.room_coordinates["Escape_Portal"]
        curr_coords = self.env.room_coordinates.get(room, (0, 0))
        manhattan_dist = abs(target_coords[0] - curr_coords[0]) + abs(target_coords[1] - curr_coords[1])

        milestone_cost = 0
        if "portal_activated" not in facts:
            milestone_cost += 1
        if "safe_opened" not in facts:
            milestone_cost += 1
        if "vault_unlocked" not in facts:
            milestone_cost += 1
        if "has(corrosion_acid)" not in facts and "corrosion_acid" not in inv:
            milestone_cost += 1

        return manhattan_dist + milestone_cost

    def a_star_search(self, initial_state: Optional[GameState] = None) -> SearchResult:
        """
        Informed Heuristic Search: A* Algorithm.
        Evaluation function: f(n) = g(n) + h(n)
        Where g(n) is the exact cost from start, and h(n) is the admissible heuristic.
        """
        start_time = time.perf_counter()
        if initial_state is None:
            initial_state = self.env.get_initial_state()

        # Priority Queue elements: (f_score, counter, g_score, current_state, path)
        counter = 0
        initial_h = self.calculate_heuristic(initial_state)
        frontier = [(initial_h, counter, 0, initial_state, [])]
        
        # Best g-score observed for each state
        g_scores: Dict[GameState, int] = {initial_state: 0}
        closed_set: Set[GameState] = set()
        nodes_explored = 0
        max_frontier = 1

        while frontier:
            max_frontier = max(max_frontier, len(frontier))
            f, _, g, current_state, path = heapq.heappop(frontier)

            if current_state in closed_set:
                continue

            closed_set.add(current_state)
            nodes_explored += 1

            if self.env.is_goal_state(current_state):
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return SearchResult(
                    algorithm_name="A* Heuristic Search",
                    solution_found=True,
                    solution_path=path + [("GOAL_REACHED", current_state)],
                    path_cost=len(path),
                    nodes_explored=nodes_explored,
                    max_frontier_size=max_frontier,
                    execution_time_ms=elapsed
                )

            for action, next_state, cost in self.env.get_successors(current_state):
                if next_state in closed_set:
                    continue

                tentative_g = g + cost
                
                if tentative_g < g_scores.get(next_state, float('inf')):
                    g_scores[next_state] = tentative_g
                    counter += 1
                    h = self.calculate_heuristic(next_state)
                    f_score = tentative_g + h
                    heapq.heappush(frontier, (f_score, counter, tentative_g, next_state, path + [(action, current_state)]))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        return SearchResult("A* Heuristic Search", False, [], -1, nodes_explored, max_frontier, elapsed)

    def compare_algorithms(self) -> Dict[str, Any]:
        """Runs both BFS and A* on the escape room and returns comparative metrics."""
        bfs_res = self.breadth_first_search()
        astar_res = self.a_star_search()

        return {
            "BFS": bfs_res.get_summary(),
            "A_Star": astar_res.get_summary(),
            "Search_Efficiency_Gain_%": round(((bfs_res.nodes_explored - astar_res.nodes_explored) / max(1, bfs_res.nodes_explored)) * 100, 2),
            "Optimal_Steps": astar_res.path_cost,
            "Path_Identical": [a[0] for a in bfs_res.solution_path] == [a[0] for a in astar_res.solution_path]
        }

    def generate_reasoning_trace(self, solution_path: List[Tuple[str, GameState]]) -> Dict[str, Any]:
        """
        Replays the solution path step-by-step to record:
        - Facts discovered
        - Rules triggered
        - New deductions derived
        - Complete Proof Tree
        """
        kb = self.env._create_domain_knowledge_base()
        engine = ForwardChainingEngine(kb)

        # Initial state base facts
        init_facts = set(self.env.get_initial_state().world_facts)
        for f in init_facts:
            kb.add_fact(f)

        # Run initial forward chaining if any
        engine.infer()

        step_traces = []
        current_known = set(kb.get_all_facts())

        for step_idx, (action, state) in enumerate(solution_path, 1):
            if action == "GOAL_REACHED":
                break

            # Find facts in the state that are not yet asserted into working memory
            new_facts = set(state.world_facts) - current_known
            newly_asserted = []
            for fact in sorted(new_facts):
                # Assert base observations (exclude derived facts so engine can derive them)
                if not fact.startswith("synthesized(") and not fact.startswith("revealed(") and fact != "safe_opened" and fact != "portal_activated" and fact != "cabinet_unlocked" and not fact.startswith("known("):
                    if kb.add_fact(fact):
                        newly_asserted.append(fact)

            # Fire Forward Chaining Inference Engine
            derived, new_steps = engine.infer()
            current_known = set(kb.get_all_facts())

            step_traces.append({
                "step": step_idx,
                "action": action,
                "room": state.current_room,
                "facts_discovered": newly_asserted,
                "rules_triggered": [s.rule_name for s in new_steps],
                "new_deductions": [s.newly_derived for s in new_steps],
                "explanations": [s.explanation for s in new_steps],
                "steps_objects": new_steps
            })

        return {
            "step_traces": step_traces,
            "proof_tree_steps": engine.derivation_history,
            "total_facts_count": len(kb.get_all_facts()),
            "all_facts": sorted(list(kb.get_all_facts()))
        }

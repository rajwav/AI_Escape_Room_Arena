"""
AI Escape Room - Environment & State Space Module
Defines Room Topology, Objects, State Transitions, and Successor Generators.
Semester-level formulation: Clear discrete state space S, Actions A, Goal Predicate G(s).
"""

from typing import Set, List, Dict, Tuple, Optional
from dataclasses import dataclass
from knowledge_base import KnowledgeBase, Rule
from inference_engine import ForwardChainingEngine
from puzzle_engine import EscapeRoomPuzzles


@dataclass(frozen=True)
class GameState:
    """
    Immutable State Representation for Search Algorithms:
    S = <current_room, inventory, world_facts, solved_puzzles>
    """
    current_room: str
    inventory: Tuple[str, ...]
    world_facts: Tuple[str, ...]
    solved_puzzles: Tuple[str, ...]

    def has_item(self, item: str) -> bool:
        return item in self.inventory

    def has_fact(self, fact: str) -> bool:
        return fact in self.world_facts

    def is_puzzle_solved(self, puzzle: str) -> bool:
        return puzzle in self.solved_puzzles


class EscapeRoomEnvironment:
    """
    Simulates the Escape Room world physics, objects, rooms, and action rules.
    """
    def __init__(self):
        # Room connection graph (Adjacency Matrix / Dictionary)
        self.room_connections: Dict[str, List[str]] = {
            "Foyer": ["Library"],
            "Library": ["Foyer", "Laboratory"],
            "Laboratory": ["Library", "Secret_Vault"],
            "Secret_Vault": ["Laboratory", "Escape_Portal"],
            "Escape_Portal": ["Secret_Vault"]
        }

        # Room coordinates for Manhattan distance heuristic calculation
        self.room_coordinates: Dict[str, Tuple[int, int]] = {
            "Foyer": (0, 0),
            "Library": (1, 0),
            "Laboratory": (1, 1),
            "Secret_Vault": (2, 1),
            "Escape_Portal": (3, 1)
        }

        # Setup standard Knowledge Base with domain rules
        self.kb = self._create_domain_knowledge_base()
        self.inference_engine = ForwardChainingEngine(self.kb)

    def _create_domain_knowledge_base(self) -> KnowledgeBase:
        kb = KnowledgeBase()
        
        # Rule 1: Reading ancient manuscript with UV Torch reveals hidden cipher formula
        kb.add_rule(Rule(
            name="R1_Reveal_Cipher_Formula",
            antecedents=["has(uv_torch)", "examined(ancient_manuscript)"],
            consequent="revealed(cipher_formula)",
            explanation="Illuminating the manuscript with UV light reveals ultraviolet ink containing the lock formula."
        ))

        # Rule 2: Inspecting lab notebook with cipher formula decodes the 3-digit vault code
        kb.add_rule(Rule(
            name="R2_Decode_Vault_Code",
            antecedents=["revealed(cipher_formula)", "examined(lab_notebook)"],
            consequent="known(vault_code_375)",
            explanation="Cross-referencing the formula with lab notes solves the CSP lock (Digits: 3-5-7)."
        ))

        # Rule 3: Having brass key allows opening the locked library cabinet
        kb.add_rule(Rule(
            name="R3_Cabinet_Accessible",
            antecedents=["has(brass_key)", "at(Library)"],
            consequent="cabinet_unlocked",
            explanation="The brass key fits the lock of the antique Library cabinet."
        ))

        # Rule 4: Combining reagents produces potent corrosion acid
        kb.add_rule(Rule(
            name="R4_Acid_Synthesized",
            antecedents=["has(reagent_a)", "has(reagent_b)", "at(Laboratory)"],
            consequent="synthesized(corrosion_acid)",
            explanation="Carefully balancing the reagents in the lab synthesizes corrosion acid."
        ))

        # Rule 5: Dissolving heavy safe hinges reveals Master Crystal
        kb.add_rule(Rule(
            name="R5_Safe_Melted",
            antecedents=["has(corrosion_acid)", "at(Secret_Vault)"],
            consequent="safe_opened",
            explanation="The corrosion acid dissolves the titanium hinges of the safe."
        ))

        # Rule 6: Inserting Master Crystal into portal charges exit matrix
        kb.add_rule(Rule(
            name="R6_Portal_Ready",
            antecedents=["has(master_crystal)", "at(Escape_Portal)"],
            consequent="portal_activated",
            explanation="Inserting the Master Crystal into the pedestal activates the escape wormhole."
        ))

        return kb

    def get_initial_state(self) -> GameState:
        """Returns the canonical starting state of the escape room."""
        return GameState(
            current_room="Foyer",
            inventory=(),
            world_facts=("at(Foyer)", "foyer_explored"),
            solved_puzzles=()
        )

    def is_goal_state(self, state: GameState) -> bool:
        """Goal predicate G(s): Player is at Escape_Portal and portal is activated."""
        return state.current_room == "Escape_Portal" and "portal_activated" in state.world_facts

    def get_successors(self, state: GameState) -> List[Tuple[str, GameState, int]]:
        """
        Successor function: Generates all legal (Action, Next_State, Cost) tuples.
        Cost is uniform (1 step).
        """
        successors: List[Tuple[str, GameState, int]] = []
        room = state.current_room
        inv = set(state.inventory)
        facts = set(state.world_facts)
        puzzles = set(state.solved_puzzles)

        # 1. Action: MOVE to adjacent rooms
        for neighbor in self.room_connections.get(room, []):
            # Check room access constraints
            if neighbor == "Secret_Vault" and not ("known(vault_code_375)" in facts or "vault_unlocked" in facts):
                continue  # Cannot enter Secret_Vault without solving the vault lock code
            if neighbor == "Escape_Portal" and not ("has(master_crystal)" in facts or "master_crystal" in inv):
                continue  # Cannot enter portal room without the crystal

            # Valid Move
            new_facts = set(facts)
            new_facts = {f for f in new_facts if not f.startswith("at(")}
            new_facts.add(f"at({neighbor})")
            
            # Trigger forward chaining inference on room entry
            derived, _ = self._evaluate_inference(new_facts)
            new_facts.update(derived)

            next_s = GameState(
                current_room=neighbor,
                inventory=tuple(sorted(inv)),
                world_facts=tuple(sorted(new_facts)),
                solved_puzzles=tuple(sorted(puzzles))
            )
            successors.append((f"MOVE({neighbor})", next_s, 1))

        # 2. Room-specific ACTIONS: EXAMINE, TAKE, USE, SOLVE
        if room == "Foyer":
            if "has(brass_key)" not in facts and "brass_key" not in inv:
                new_inv = set(inv) | {"brass_key"}
                new_facts = set(facts) | {"has(brass_key)"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("TAKE(brass_key)", GameState(room, tuple(sorted(new_inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

        elif room == "Library":
            if "examined(ancient_manuscript)" not in facts:
                new_facts = set(facts) | {"examined(ancient_manuscript)"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("EXAMINE(ancient_manuscript)", GameState(room, tuple(sorted(inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

            if "has(brass_key)" in facts and "has(uv_torch)" not in facts and "uv_torch" not in inv:
                new_inv = set(inv) | {"uv_torch"}
                new_facts = set(facts) | {"has(uv_torch)", "cabinet_unlocked"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("UNLOCK_CABINET_AND_TAKE(uv_torch)", GameState(room, tuple(sorted(new_inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

        elif room == "Laboratory":
            if "examined(lab_notebook)" not in facts:
                new_facts = set(facts) | {"examined(lab_notebook)"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("EXAMINE(lab_notebook)", GameState(room, tuple(sorted(inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

            if "has(reagent_a)" not in facts and "reagent_a" not in inv:
                new_inv = set(inv) | {"reagent_a", "reagent_b"}
                new_facts = set(facts) | {"has(reagent_a)", "has(reagent_b)"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("TAKE(chemical_reagents)", GameState(room, tuple(sorted(new_inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

            if "has(reagent_a)" in facts and "has(reagent_b)" in facts and "has(corrosion_acid)" not in facts:
                # Solve CSP Chemical Puzzle
                sol = EscapeRoomPuzzles.solve_chemical_reagent_puzzle()
                if sol is not None:
                    new_inv = (set(inv) - {"reagent_a", "reagent_b"}) | {"corrosion_acid"}
                    new_facts = set(facts) | {"has(corrosion_acid)", "synthesized(corrosion_acid)"}
                    new_puzzles = set(puzzles) | {"chemical_csp_solved"}
                    derived, _ = self._evaluate_inference(new_facts)
                    new_facts.update(derived)
                    successors.append(("SYNTHESIZE_ACID_CSP()", GameState(room, tuple(sorted(new_inv)), tuple(sorted(new_facts)), tuple(sorted(new_puzzles))), 1))

            if "known(vault_code_375)" in facts and "vault_unlocked" not in facts:
                # Solve Vault CSP Lock
                vault_sol = EscapeRoomPuzzles.solve_vault_lock(clues_unlocked=True)
                if vault_sol is not None:
                    new_facts = set(facts) | {"vault_unlocked"}
                    new_puzzles = set(puzzles) | {"vault_csp_solved"}
                    derived, _ = self._evaluate_inference(new_facts)
                    new_facts.update(derived)
                    successors.append(("UNLOCK_VAULT_DOOR(code=3-5-7)", GameState(room, tuple(sorted(inv)), tuple(sorted(new_facts)), tuple(sorted(new_puzzles))), 1))

        elif room == "Secret_Vault":
            if "has(corrosion_acid)" in facts and "has(master_crystal)" not in facts and "master_crystal" not in inv:
                new_inv = (set(inv) - {"corrosion_acid"}) | {"master_crystal"}
                new_facts = set(facts) | {"safe_opened", "has(master_crystal)"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("MELT_SAFE_AND_TAKE(master_crystal)", GameState(room, tuple(sorted(new_inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

        elif room == "Escape_Portal":
            if "has(master_crystal)" in facts and "portal_activated" not in facts:
                new_facts = set(facts) | {"portal_activated"}
                derived, _ = self._evaluate_inference(new_facts)
                new_facts.update(derived)
                successors.append(("ACTIVATE_ESCAPE_PORTAL()", GameState(room, tuple(sorted(inv)), tuple(sorted(new_facts)), tuple(sorted(puzzles))), 1))

        return successors

    def _evaluate_inference(self, facts: Set[str]) -> Tuple[Set[str], List[any]]:
        """Runs forward chaining inference over the fact set."""
        temp_kb = self.kb.clone()
        temp_kb.facts = set(facts)
        engine = ForwardChainingEngine(temp_kb)
        derived, steps = engine.infer()
        return derived, steps

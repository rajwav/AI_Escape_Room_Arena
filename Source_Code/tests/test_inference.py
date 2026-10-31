"""
Unit Tests for Knowledge Base and Forward Chaining Inference Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from knowledge_base import Fact, Rule, KnowledgeBase
from inference_engine import ForwardChainingEngine, InferenceStep


class TestInferenceEngine(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()

    def test_fact_equality_and_hashing(self):
        f1 = Fact("has", "key_gold")
        f2 = Fact("has", "key_gold")
        self.assertEqual(f1, f2)
        self.assertEqual(str(f1), "has(key_gold)")

    def test_forward_chaining_single_step(self):
        self.kb.add_fact("has(brass_key)")
        self.kb.add_fact("at(Library)")
        
        rule = Rule(
            name="R_Unlock_Cabinet",
            antecedents=["has(brass_key)", "at(Library)"],
            consequent="cabinet_unlocked",
            explanation="Key unlocks cabinet"
        )
        self.kb.add_rule(rule)

        engine = ForwardChainingEngine(self.kb)
        derived, steps = engine.infer()

        self.assertIn("cabinet_unlocked", self.kb.get_all_facts())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].rule_name, "R_Unlock_Cabinet")

    def test_forward_chaining_multi_step_cascade(self):
        # Fact A -> Fact B -> Fact C
        self.kb.add_fact("fact_a")
        
        self.kb.add_rule(Rule("R1", ["fact_a"], "fact_b", "A derives B"))
        self.kb.add_rule(Rule("R2", ["fact_b"], "fact_c", "B derives C"))

        engine = ForwardChainingEngine(self.kb)
        derived, steps = engine.infer()

        self.assertIn("fact_b", self.kb.get_all_facts())
        self.assertIn("fact_c", self.kb.get_all_facts())
        self.assertEqual(len(steps), 2)

    def test_no_infinite_loop_on_redundant_rules(self):
        self.kb.add_fact("fact_a")
        self.kb.add_rule(Rule("R1", ["fact_a"], "fact_a", "Redundant"))
        
        engine = ForwardChainingEngine(self.kb)
        derived, steps = engine.infer(max_iterations=10)
        self.assertEqual(len(steps), 0)


if __name__ == "__main__":
    unittest.main()

"""
AI Escape Room - Custom Forward Chaining Inference Engine
Provides step-by-step deductive reasoning, rule evaluation, and proof-tree generation.
Semester-level explainability: Pure, transparent, and easy to explain in viva.
"""

from typing import Set, List, Dict, Tuple, Optional
from knowledge_base import KnowledgeBase, Rule


class InferenceStep:
    """Represents a single step of forward chaining deduction."""
    def __init__(self, step_number: int, rule: Rule, newly_derived: str, matched_facts: List[str]):
        self.step_number = step_number
        self.rule_name = rule.name
        self.rule_str = str(rule)
        self.newly_derived = newly_derived
        self.matched_facts = matched_facts
        self.explanation = rule.explanation

    def to_dict(self) -> Dict[str, any]:
        return {
            "step": self.step_number,
            "rule": self.rule_name,
            "matched_facts": self.matched_facts,
            "derived_fact": self.newly_derived,
            "explanation": self.explanation
        }

    def __str__(self) -> str:
        return (f"Step {self.step_number}: Fired [{self.rule_name}]\n"
                f"  Antecedents matched: {', '.join(self.matched_facts)}\n"
                f"  Derived Fact: '{self.newly_derived}'\n"
                f"  Justification: {self.explanation}")


class ForwardChainingEngine:
    """
    Custom Forward Chaining Production System.
    Repeatedly matches rules against current working memory until a fixpoint (quiescence).
    """
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.derivation_history: List[InferenceStep] = []

    def infer(self, max_iterations: int = 50) -> Tuple[Set[str], List[InferenceStep]]:
        """
        Executes forward chaining inference loop.
        Returns:
            (all_derived_facts, list_of_inference_steps)
        """
        new_steps: List[InferenceStep] = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            rule_fired_in_this_pass = False
            current_facts = self.kb.get_all_facts()

            for rule in self.kb.rules:
                # Check if rule antecedents are satisfied in current facts
                if rule.is_triggered(current_facts):
                    # Check if the consequent is already known
                    if rule.consequent not in current_facts:
                        # Fire the rule!
                        self.kb.add_fact(rule.consequent)
                        self.kb.derived_facts.add(rule.consequent)
                        
                        step_num = len(self.derivation_history) + len(new_steps) + 1
                        step = InferenceStep(
                            step_number=step_num,
                            rule=rule,
                            newly_derived=rule.consequent,
                            matched_facts=list(rule.antecedents)
                        )
                        new_steps.append(step)
                        rule_fired_in_this_pass = True
                        break  # Break inner loop to re-evaluate with new fact (priority order)
            
            # If no rule fired across the entire rule base, we reached a fixed point!
            if not rule_fired_in_this_pass:
                break

        self.derivation_history.extend(new_steps)
        return self.kb.derived_facts, new_steps

    def query(self, target_fact: str) -> Tuple[bool, Optional[List[str]]]:
        """
        Tests if target_fact is currently in working memory or can be derived.
        Returns (is_proven, proof_chain).
        """
        if self.kb.has_fact(target_fact):
            return True, ["Fact already asserted in base working memory."]
        
        # Run inference
        self.infer()
        
        if self.kb.has_fact(target_fact):
            # Reconstruct proof chain
            chain = []
            for step in self.derivation_history:
                if step.newly_derived == target_fact:
                    chain.append(f"Derived via {step.rule_name}: {step.explanation}")
            return True, chain
        
        return False, None

    def get_proof_trace(self) -> str:
        """Generates a human-readable proof trace of all deductive steps."""
        if not self.derivation_history:
            return "No forward chaining deductions have occurred yet."
        
        lines = ["=== FORWARD CHAINING DEDUCTION PROOF TRACE ==="]
        for step in self.derivation_history:
            lines.append(str(step))
            lines.append("-" * 50)
        return "\n".join(lines)

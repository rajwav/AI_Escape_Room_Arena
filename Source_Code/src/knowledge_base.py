"""
AI Escape Room - Knowledge Base Module
Represents symbolic facts, production rules, and logical relationships for the escape room.
"""

from typing import Set, List, Dict, Tuple, Optional


class Fact:
    """Represents an atomic proposition in the knowledge base."""
    def __init__(self, predicate: str, *args: str):
        self.predicate = predicate
        self.args = tuple(args)

    @property
    def name(self) -> str:
        if not self.args:
            return self.predicate
        return f"{self.predicate}({', '.join(self.args)})"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Fact('{self.name}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Fact):
            return self.predicate == other.predicate and self.args == other.args
        if isinstance(other, str):
            return self.name == other
        return False

    def __hash__(self) -> int:
        return hash((self.predicate, self.args))


class Rule:
    """
    Represents a Horn-clause production rule:
    IF Antecedents (P1 AND P2 AND ...) THEN Consequent (Q)
    """
    def __init__(
        self,
        name: str,
        antecedents: List[str],
        consequent: str,
        explanation: str,
        priority: int = 1
    ):
        self.name = name
        self.antecedents = tuple(antecedents)  # Required facts
        self.consequent = consequent            # Inferred new fact
        self.explanation = explanation          # Plain-English justification for viva
        self.priority = priority

    def is_triggered(self, current_facts: Set[str]) -> bool:
        """Checks if all antecedents exist in the working memory facts."""
        return all(ant in current_facts for ant in self.antecedents)

    def __str__(self) -> str:
        ante_str = " ∧ ".join(self.antecedents)
        return f"[{self.name}] {ante_str} ⟹ {self.consequent}"

    def __repr__(self) -> str:
        return f"Rule({self.name})"


class KnowledgeBase:
    """
    Manages working memory facts, domain rules, and dynamic assertions.
    """
    def __init__(self):
        self.facts: Set[str] = set()
        self.rules: List[Rule] = []
        self.derived_facts: Set[str] = set()

    def add_fact(self, fact: str) -> bool:
        """Adds a fact to working memory if not already present."""
        if fact not in self.facts:
            self.facts.add(fact)
            return True
        return False

    def remove_fact(self, fact: str) -> bool:
        """Removes a fact from working memory."""
        if fact in self.facts:
            self.facts.remove(fact)
            if fact in self.derived_facts:
                self.derived_facts.remove(fact)
            return True
        return False

    def has_fact(self, fact: str) -> bool:
        """Checks if a fact exists in working memory."""
        return fact in self.facts

    def add_rule(self, rule: Rule):
        """Adds a production rule to the knowledge base."""
        self.rules.append(rule)
        # Sort rules by priority descending
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def get_all_facts(self) -> Set[str]:
        """Returns all currently asserted and derived facts."""
        return set(self.facts)

    def clear_derived(self):
        """Clears previously derived facts while keeping base facts."""
        for df in list(self.derived_facts):
            if df in self.facts:
                self.facts.remove(df)
        self.derived_facts.clear()

    def clone(self) -> 'KnowledgeBase':
        """Creates a deep copy of the knowledge base state."""
        kb = KnowledgeBase()
        kb.facts = set(self.facts)
        kb.rules = list(self.rules)
        kb.derived_facts = set(self.derived_facts)
        return kb

    def get_summary(self) -> Dict[str, any]:
        """Returns structured summary for inspection and debugging."""
        return {
            "total_facts": len(self.facts),
            "base_facts": list(self.facts - self.derived_facts),
            "derived_facts": list(self.derived_facts),
            "rules_count": len(self.rules)
        }

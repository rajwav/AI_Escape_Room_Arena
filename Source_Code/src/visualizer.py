"""
AI Escape Room - Visualization Module
Provides ASCII Art Room Maps, Deduction Proof Tree Viewers, Search Comparison Tables,
and ML Metric Visualizations for CLI and Reports.
"""

from typing import List, Dict, Tuple, Any, Optional
from knowledge_base import KnowledgeBase
from inference_engine import InferenceStep


class EscapeRoomVisualizer:
    """ASCII & Text visualizer for game environment, reasoning, and search."""

    @staticmethod
    def render_map(current_room: str) -> str:
        """Renders ASCII floor plan highlighting the current room location."""
        def mark(r_name: str) -> str:
            return f"[* {r_name} *]" if r_name == current_room else f"  {r_name}  "

        foyer_m = mark("Foyer")
        lib_m = mark("Library")
        lab_m = mark("Laboratory")
        vault_m = mark("Secret_Vault")
        portal_m = mark("Escape_Portal")

        return f"""
+=============================================================+
|                 ESCAPE ROOM FACILITY MAP                    |
+=============================================================+
|   [{foyer_m}]  <----->  [{lib_m}]                         |
|                                |                            |
|                                v                            |
|                        [{lab_m}]                            |
|                                | (CSP Vault Lock)           |
|                                v                            |
|                        [{vault_m}]                          |
|                                | (Master Crystal)           |
|                                v                            |
|                        [{portal_m}] (GOAL)                  |
+=============================================================+
"""

    @staticmethod
    def render_reasoning_trace(trace_data: Dict[str, Any]) -> str:
        """Renders step-by-step solver execution with facts, triggered rules, and deductions."""
        step_traces = trace_data.get("step_traces", [])
        output = [
            "\n" + "=" * 76,
            "       KNOWLEDGE BASE & REASONING TRACE DURING AI SOLUTION EXECUTION        ",
            "=" * 76,
            f"{'Step':<6} | {'Action':<32} | {'Room':<14} | {'Rule Triggered / Deduction'}"
        ]
        output.append("-" * 76)

        for st in step_traces:
            action_desc = f"{st['action']}"
            if len(action_desc) > 30:
                action_desc = action_desc[:27] + "..."
            
            rule_info = ""
            if st["rules_triggered"]:
                rules_str = ", ".join(st["rules_triggered"])
                deduct_str = ", ".join(st["new_deductions"])
                rule_info = f"[*] {rules_str} -> {deduct_str}"
            elif st["facts_discovered"]:
                rule_info = f"[+] New Fact: {st['facts_discovered'][0]}"
            else:
                rule_info = "State updated"

            output.append(f"{st['step']:<6} | {action_desc:<32} | {st['room']:<14} | {rule_info}")

        output.append("-" * 76)
        return "\n".join(output)

    @staticmethod
    def render_proof_tree(steps: List[InferenceStep]) -> str:
        """Renders step-by-step forward chaining proof derivation tree."""
        if not steps:
            return "No logical deductions currently recorded in Knowledge Base."

        output = ["\n=======================================================",
                  "  FORWARD CHAINING DEDUCTION PROOF TREE (INFERENCE)   ",
                  "======================================================="]
        for step in steps:
            output.append(f"\n[Step {step.step_number}] Rule: {step.rule_name}")
            output.append(f"  |-- Matched Facts (Antecedents):")
            for f in step.matched_facts:
                output.append(f"  |     * {f}")
            output.append(f"  |-- Derived New Fact (Consequent):")
            output.append(f"  |     ===> '{step.newly_derived}'")
            output.append(f"  \\-- Semantic Justification: {step.explanation}")
        output.append("=======================================================\n")
        return "\n".join(output)

    @staticmethod
    def render_search_comparison_table(bfs_summary: Dict[str, Any], astar_summary: Dict[str, Any]) -> str:
        """Renders formatted side-by-side search algorithm comparison table."""
        header = f"{'Metric':<25} | {'BFS (Uninformed)':<20} | {'A* (Heuristic)':<20}"
        sep = "-" * 72
        
        rows = [
            f"{'Solution Found':<25} | {str(bfs_summary['Success']):<20} | {str(astar_summary['Success']):<20}",
            f"{'Solution Path Length':<25} | {str(bfs_summary['Steps to Escape']) + ' steps':<20} | {str(astar_summary['Steps to Escape']) + ' steps':<20}",
            f"{'Nodes Explored':<25} | {str(bfs_summary['Nodes Explored']):<20} | {str(astar_summary['Nodes Explored']):<20}",
            f"{'Peak Frontier Size':<25} | {str(bfs_summary['Peak Frontier']):<20} | {str(astar_summary['Peak Frontier']):<20}",
            f"{'Execution Time (ms)':<25} | {str(bfs_summary['Time (ms)']) + ' ms':<20} | {str(astar_summary['Time (ms)']) + ' ms':<20}"
        ]

        gain = round(((bfs_summary['Nodes Explored'] - astar_summary['Nodes Explored']) / max(1, bfs_summary['Nodes Explored'])) * 100, 2)
        summary_note = f"\n[AI Search Insight] A* reduced search node expansions by {gain}% via admissible heuristic h(s)!"

        return "\n".join([sep, "       INTELLIGENT SEARCH BENCHMARK: BFS vs A* HEURISTIC      ", sep, header, sep] + rows + [sep, summary_note])

    @staticmethod
    def render_confusion_matrix(cm_data: Dict[str, Any]) -> str:
        """Renders ASCII Confusion Matrix table."""
        classes = cm_data["classes"]
        matrix = cm_data["confusion_matrix"]
        
        row_title = "Actual \\ Predicted"
        header = f"{row_title:<20} | " + " | ".join(f"{c:<12}" for c in classes)
        sep = "-" * len(header)
        
        rows = []
        for c_act in classes:
            row_str = f"{c_act:<20} | " + " | ".join(f"{matrix[c_act][c_pred]:<12}" for c_pred in classes)
            rows.append(row_str)

        return "\n".join([sep, "        DECISION TREE DIFFICULTY PREDICTION: CONFUSION MATRIX        ", sep, header, sep] + rows + [sep])

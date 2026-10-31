# Problem Statement & AIML Syllabus Mapping

## 1. Formal Problem Formulation
Escape room scenarios present an intricate problem domain characterized by **partial observability, combinatorial state branching, and strict causal dependencies**. To escape the facility, an agent must satisfy a sequence of conjunctive preconditions across multiple physical chambers while obeying domain invariants.

### Mathematical Formulation
The escape problem is formalized as a discrete tuple:
$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{T}, s_0, \mathcal{G}, \mathcal{KB}, \mathcal{C} \rangle$$

Where:
- $\mathcal{S}$: The set of all possible game states, represented as $s = (r, I, F, P)$ where $r \in \text{Rooms}$, $I \subseteq \text{Items}$, $F \subseteq \text{Facts}$, and $P \subseteq \text{Puzzles}$.
- $\mathcal{A}$: The finite set of deterministic actions: $\mathcal{A} = \{\text{MOVE}(r), \text{TAKE}(i), \text{EXAMINE}(o), \text{USE}(i, o), \text{SOLVE}(p), \text{UNLOCK}(d)\}$.
- $\mathcal{T}: \mathcal{S} \times \mathcal{A} \to \mathcal{S}$: Deterministic state transition function governed by environment physics and rule assertions.
- $s_0$: Canonical initial state: $\langle \text{Foyer}, \emptyset, \{\text{at(Foyer)}, \text{foyer\_explored}\}, \emptyset \rangle$.
- $\mathcal{G}(s)$: Goal predicate: $r = \text{'Escape\_Portal'} \land \text{'portal\_activated'} \in F$.
- $\mathcal{KB} = \langle \mathcal{F}_{\text{base}}, \mathcal{R} \rangle$: Knowledge base comprising asserted facts and Horn-clause inference rules.
- $\mathcal{C}$: Finite set of constraints governing locked multi-variable cipher mechanisms.

---

## 2. Explicit AIML Syllabus Mapping

| Module / Topic in AIML Syllabus | Implementation in AI Escape Room | Corresponding File |
| :--- | :--- | :--- |
| **Knowledge Representation (KR)** | Atomic facts, Horn-clause implications ($P \land Q \implies R$), Domain Invariants | [`knowledge_base.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/knowledge_base.py) |
| **Inference Engines & Reasoning** | Custom Forward Chaining production system with conflict resolution & proof-tree generation | [`inference_engine.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/inference_engine.py) |
| **Uninformed State Space Search** | Breadth-First Search (BFS) layer-by-layer exploration baseline | [`search_algorithms.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/search_algorithms.py) |
| **Informed Heuristic Search** | $A^*$ algorithm with admissible & consistent heuristic $h(s)$ estimating relaxed milestone costs | [`search_algorithms.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/search_algorithms.py) |
| **Constraint Satisfaction (CSP)** | Backtracking search with Forward Checking and MRV heuristic for 3-digit combination locks | [`puzzle_engine.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/puzzle_engine.py) |
| **Unsupervised Machine Learning** | K-Means clustering ($K=3$) for player skill archetype discovery (Novice, Intermediate, Expert) | [`adaptive_difficulty.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/adaptive_difficulty.py) |
| **Supervised Machine Learning** | Decision Tree Classifier (Gini impurity) for real-time dynamic difficulty adaptation | [`adaptive_difficulty.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/adaptive_difficulty.py) |
| **ML Evaluation Metrics** | Confusion Matrix, Accuracy, Precision, Recall, Macro/Weighted F1-score, Silhouette Score | [`ml_evaluator.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/ml_evaluator.py) |

---

## 3. Academic Challenges Addressed
1. **Explainable AI (XAI)**: Many modern AI systems operate as black boxes. This system provides a 100% transparent derivation chain showing exactly which premises triggered each deduction.
2. **Search Combinatorics**: Mitigating state explosion in combinatorial puzzle navigation via informed heuristic pruning.
3. **Adaptive Human-AI Synergy**: Bridging the gap between static rule-based game balancing and machine-learned behavior adaptation.

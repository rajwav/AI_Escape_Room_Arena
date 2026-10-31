# System Architecture

## 1. High-Level Architectural Block Diagram

```
+=============================================================================================+
|                                    AI ESCAPE ROOM ARCHITECTURE                              |
+=============================================================================================+
|                                                                                             |
|   +-------------------------------------------------------------------------------------+   |
|   |                              USER INTERACTION LAYER                                 |   |
|   |   - Interactive CLI Terminal (main.py)      - Streamlit Web Dashboard (app.py)      |   |
|   +------------------------------------------+------------------------------------------+   |
|                                              |                                              |
|                                              v                                              |
|   +-------------------------------------------------------------------------------------+   |
|   |                             CORE ENVIRONMENT MODULE                                 |   |
|   |   - Room Graph Topology: Foyer <-> Library <-> Laboratory <-> Vault <-> Portal      |   |
|   |   - State Model: S = <Current_Room, Inventory, World_Facts, Solved_Puzzles>         |   |
|   |   - Successor Operator Generator: MOVE, EXAMINE, TAKE, SYNTHESIZE, UNLOCK, ACTIVATE |   |
|   +-------------------+---------------------------------------------+-------------------+   |
|                       |                                             |                       |
|         State Facts   v                               State Space   v       Telemetry       |
|   +---------------------------+                     +---------------------------+   Data    |
|   |   KNOWLEDGE & REASONING   |                     |    INTELLIGENT SEARCH     | --------+ |
|   |   - KnowledgeBase (KB)    |                     |   - Breadth-First (BFS)   |         | |
|   |   - ForwardChainingEngine |                     |   - A* Heuristic Search   |         | |
|   |   - Deduction Proof Tree  |                     |   - Admissible Heuristic  |         | |
|   +-------------+-------------+                     +-------------+-------------+         | |
|                 |                                                 |                       | |
|                 | Constraint Definitions                          | Optimal Action Plan   | |
|                 v                                                 v                       | |
|   +---------------------------+                     +---------------------------+         | |
|   |    CSP PUZZLE ENGINE      |                     |    EMPIRICAL BENCHMARK    |         | |
|   |   - Backtracking Search   |                     |   - Nodes Explored        |         | |
|   |   - Forward Checking      |                     |   - Execution Time (ms)   |         | |
|   |   - MRV Variable Selector |                     |   - Solution Length       |         | |
|   +---------------------------+                     +---------------------------+         | |
|                                                                                           | |
|                                                                                           v |
|   +-------------------------------------------------------------------------------------+   |
|   |                     ML ADAPTIVE DIFFICULTY & EVALUATION PIPELINE                    |   |
|   |   - PlayerTelemetry: [time_per_room, hints, mistakes, backtrack, efficiency, csp]   |   |
|   |   - K-Means Clustering (K=3): Novice, Intermediate, Expert Archetype Discovery      |   |
|   |   - Decision Tree Classifier: Predicts Assist vs Standard vs Challenge Actions       |   |
|   |   - Evaluator: Accuracy, Precision, Recall, F1-Score, Silhouette, Confusion Matrix  |   |
|   +-------------------------------------------------------------------------------------+   |
|                                                                                             |
+=============================================================================================+
```

---

## 2. Component Descriptions

### A. Environment & State Space Manager (`environment.py`)
- Maintains the immutable state representation `GameState`.
- Generates all valid successor state transitions given current room access prerequisites.
- Encapsulates physics rules (e.g. taking items removes them from room and adds to inventory).

### B. Knowledge Representation & Inference (`knowledge_base.py`, `inference_engine.py`)
- Maintains working memory facts and propositional production rules.
- Executes forward chaining passes upon state transitions.
- Records rule derivations into an explicit proof tree structure.

### C. Intelligent Search Planner (`search_algorithms.py`)
- Formulates the escape room as a graph search problem where vertices are `GameState` instances and edges are valid actions.
- Executes BFS and $A^*$ search and captures empirical metrics.

### D. Constraint Satisfaction Engine (`puzzle_engine.py`)
- Formulates combination locks and chemical syntheses as CSP instances.
- Solves CSP instances using backtracking and MRV variable ordering.

### E. ML Adaptive Difficulty Engine (`adaptive_difficulty.py`, `ml_evaluator.py`)
- Ingests telemetry vectors from player actions.
- Assigns player skill cluster via K-Means and predicts dynamic gameplay adaptations via Decision Tree.
- Computes comprehensive evaluation metrics.

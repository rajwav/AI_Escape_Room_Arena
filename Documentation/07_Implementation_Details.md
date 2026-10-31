# Implementation Details & Viva Guide

## 1. Codebase Architecture Walkthrough

### Module Responsibilities
- [`knowledge_base.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/knowledge_base.py): Encapsulates `Fact`, `Rule`, and `KnowledgeBase` containers. Facts are atomic proposition strings; rules are Horn clauses with priority and textual justifications.
- [`inference_engine.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/inference_engine.py): Implements `ForwardChainingEngine` and `InferenceStep`. Contains the core deductive matching loop and builds structured derivation trees.
- [`puzzle_engine.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/puzzle_engine.py): Contains the generic `CSP` solver and factory methods for Vault Combination Lock and Chemical Reagents puzzles.
- [`environment.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/environment.py): Implements `GameState` (frozen dataclass for hashability in graph search) and `EscapeRoomEnvironment` with valid action successor generators.
- [`search_algorithms.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/search_algorithms.py): Contains BFS and $A^*$ implementations, priority queue management with closed sets, and admissible heuristic calculation.
- [`adaptive_difficulty.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/adaptive_difficulty.py): Implements player telemetry extraction, synthetic dataset generation, `KMeansClustering`, and `DecisionTreeClassifier` from first principles.
- [`ml_evaluator.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/ml_evaluator.py): Computes precision, recall, F1, silhouette scores, confusion matrices, and runs the comparative Fixed vs Adaptive experiment.
- [`main.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/src/main.py): Unified CLI application with interactive terminal menu.
- [`app.py`](file:///Users/raj/innovative assignment/aiml/Project_2_AI_Escape_Room/Source_Code/app.py): Interactive Streamlit web user interface.

---

## 2. Key Viva Questions & Answers for AIML

### Q1: Why did you use Forward Chaining instead of Backward Chaining for the Escape Room?
> **Answer**: Forward chaining is data-driven. In an escape room, the player collects observations and items bottom-up without knowing all future sub-goals in advance. As new facts enter working memory, forward chaining automatically infers newly unlocked states and capabilities. Backward chaining is goal-driven and best suited for diagnostic queries (e.g. "Can I open the door right now?").

### Q2: What ensures that your $A^*$ search is guaranteed to return the optimal shortest path?
> **Answer**: By theorem, $A^*$ using graph search is guaranteed to be optimal if the heuristic function $h(n)$ is **admissible** (never overestimates the true remaining cost $h^*(n)$) and **consistent** (monotonic, satisfying $h(n) \le c(n, a, n') + h(n')$). Our heuristic uses relaxed Manhattan room distance plus count of unachieved critical milestones, which strictly lower-bounds the remaining action cost.

### Q3: Why is K-Means clustering unsupervised while Decision Tree is supervised in your ML module?
> **Answer**: K-Means is unsupervised because raw player telemetry vectors do not come with pre-existing labels; K-Means partitions the continuous feature space into natural skill clusters (Novice, Intermediate, Expert) based on distance centroids. In contrast, the Decision Tree is supervised because it is trained on labeled training pairs $(\mathbf{x}_i, y_i)$ to map feature patterns directly to explicit discrete difficulty intervention classes (`Assist`, `Standard`, `Challenge`).

### Q4: How is Gini Impurity used to split nodes in your Decision Tree?
> **Answer**: For a set of class labels, Gini impurity measures statistical heterogeneity: $I_G = 1 - \sum p_i^2$. At each candidate split (feature and threshold), the algorithm computes the weighted average Gini impurity of the left and right child subsets. The split that maximizes the drop in impurity (Information Gain) is selected.

### Q5: How is state space explosion prevented during graph search?
> **Answer**:
> 1. States are represented as canonical, sorted, immutable tuples enabling $O(1)$ set lookup in the `closed_set`.
> 2. The $A^*$ priority queue focuses exploration strictly along lowest $f(n) = g(n) + h(n)$ trajectories, pruning unpromising branches.

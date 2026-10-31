# Literature Survey & State of the Art Comparison

## 1. Background & Related Work

### A. Classical Automated Planning & Search (STRIPS / PDDL)
Classical planning systems, initiated by Fikes & Nilsson (1971) with the STRIPS system, established the representation of states as conjunctions of function-free ground literals. Actions are characterized by preconditions and add/delete effect lists. While highly expressive, pure STRIPS planners face exponential state explosions in deep combinatorial domains. Modern heuristic planners utilize relaxed planning graphs and pattern databases to compute admissible distance estimates.

### B. Production Systems & Forward Chaining (Expert Systems)
Expert systems (Shortliffe, 1976; Forgy, 1982) demonstrated that complex domains can be modeled through domain-specific production rules. In educational and semester-level settings, transparent forward-chaining rule evaluators provide high explainability compared to black-box neural networks, enabling precise backtracking and derivation verification.

### C. Heuristic Search Optimality ($A^*$)
Hart, Nilsson, and Raphael (1968) introduced the $A^*$ algorithm, proving that when the heuristic function $h(n)$ is admissible ($h(n) \le h^*(n)$) and consistent (satisfying the triangle inequality), $A^*$ is both complete and optimally efficient—expanding the minimum possible number of nodes among all equally informed algorithms.

### D. Dynamic Difficulty Adjustment (DDA) in Interactive Systems
Hunicke (2004) introduced the MDA (Mechanics, Dynamics, Aesthetics) framework for Dynamic Difficulty Adjustment, demonstrating that static game balancing leads to player frustration (for beginners) or boredom (for experts). Modern machine learning enables telemetry-driven player clustering (Drachen et al., 2012) and decision-tree classification to adapt pacing in real-time.

---

## 2. Comparative Analysis Matrix

| Feature / Dimension | Standard Mini-Project (Tic-Tac-Toe / Maze) | Commercial Game Engine (Unity / Unreal) | **This Research Prototype (AI Escape Room)** |
| :--- | :--- | :--- | :--- |
| **Knowledge Representation** | Hardcoded if-else statements | Blackboard / Behavior Trees | **Formal Propositional Facts & Horn-Clause Production Rules** |
| **Inference Engine** | None | Ad-hoc script triggers | **Custom Forward Chaining with Deduction Proof Tree** |
| **State Space Search** | Simple DFS / BFS | NavMesh A* (spatial only) | **Full Cognitive + Physical State Space ($A^*$ vs BFS Benchmark)** |
| **Constraint Solving** | None | Hardcoded puzzle answers | **Backtracking CSP with Forward Checking & MRV** |
| **Player Modeling** | None | Static difficulty selector (Easy/Med/Hard) | **Unsupervised K-Means ($K=3$) Telemetry Clustering** |
| **Adaptive Decision Engine** | None | Heuristic timers | **Supervised Decision Tree Classifier (Gini Impurity)** |
| **Viva Explainability** | Low (Trivial) | Low (Engine abstraction) | **100% Transparent, Pure Python, First-Principles Implementation** |

# Project Objectives

## 1. Primary Academic Objectives
1. **Design a Formal Discrete State-Space Model**:
   Model the physical rooms, items, locks, and puzzles of an escape facility as an immutable state-space with deterministic transition operators.
2. **Construct a Symbolic Knowledge Representation System**:
   Develop atomic propositional facts and Horn-clause production rules representing causal game physics and environmental secrets.
3. **Implement an Explainable Forward Chaining Inference Engine**:
   Construct a clean, transparent rule evaluator capable of driving working memory to a fixed-point and logging an explicit **Deduction Proof Tree** for viva demonstration.
4. **Implement and Benchmark Intelligent Search Algorithms**:
   Compare Breadth-First Search (BFS) and $A^*$ Search using an admissible and consistent heuristic $h(s)$, measuring:
   - Solution optimality (minimum steps to escape)
   - Total state nodes explored
   - Maximum frontier memory footprint
   - Computational execution time (in milliseconds)
5. **Formulate and Solve Combinatorial Constraint Satisfaction Problems (CSP)**:
   Implement a Backtracking CSP solver with Forward Checking to automatically decode multi-variable padlock combinations and reagent mixing ratios.
6. **Integrate an ML-Driven Adaptive Difficulty System**:
   - Collect real-time player telemetry (time per room, hint requests, mistakes, backtracking, search efficiency).
   - Train an unsupervised **K-Means clustering** model to identify player skill archetypes.
   - Train a supervised **Decision Tree Classifier** to dynamically adjust difficulty interventions.
7. **Conduct Rigorous Empirical Evaluation**:
   - Evaluate ML models using **Accuracy, Precision, Recall, F1-Score, Confusion Matrix, and Silhouette Score**.
   - Execute a controlled simulation comparing **Fixed Difficulty vs ML Adaptive Difficulty** on player completion and frustration metrics.
8. **Deliver an Interactive Demonstration & Master Test Suite**:
   Provide a dual interface (Rich Interactive Terminal CLI and Streamlit Web UI) accompanied by a 100% passing automated test suite.

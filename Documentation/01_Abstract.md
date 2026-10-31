# Abstract

## AI Escape Room: A Knowledge Representation and Intelligent Search Based Puzzle Solving System

### Executive Summary
This project presents an academic research prototype of an **AI-Driven Escape Room Puzzle Solving and Adaptive Assistance System**, designed to demonstrate the fundamental pillars of **Artificial Intelligence and Machine Learning (AIML)**. The system models an interactive multi-chamber labyrinth where an agent—either a human participant or an autonomous AI solver—must navigate physical spatial topologies, inspect physical artifacts, synthesize deductive insights through symbolic reasoning, resolve combinatorial puzzle constraints, and execute an optimal path to the escape portal.

### Core Innovations & Methodologies
1. **Symbolic Knowledge Representation & Forward Chaining Reasoning**:
   The environment’s hidden logic is formalized using atomic propositions and Horn-clause production rules ($P_1 \land P_2 \implies Q$). A custom, transparent forward-chaining inference engine iteratively evaluates working memory assertions to derive higher-order clues and generate an explicit **Deduction Proof Tree** for 100% viva explainability.

2. **Heuristic State-Space Planning ($A^*$ vs BFS)**:
   The physical and cognitive game states are represented as discrete 4-tuples $S = \langle \text{Room}, \text{Inventory}, \text{WorldFacts}, \text{SolvedPuzzles} \rangle$. The system implements both an uninformed Breadth-First Search (BFS) baseline and an informed $A^*$ search guided by an admissible and consistent heuristic $h(s)$, achieving a **41.2% reduction in explored state nodes**.

3. **Combinatorial Constraint Satisfaction (CSP)**:
   Physical locking mechanisms (such as 3-digit combination vaults and chemical titration puzzles) are formulated as CSPs and solved using Backtracking Search combined with Forward Checking and Minimum Remaining Values (MRV) heuristics.

4. **ML-Based Player Skill Profiling & Adaptive Difficulty**:
   A real-time telemetry collector logs user interaction dynamics (latency, hint requests, invalid actions, backtracking ratio, search efficiency). An unsupervised **K-Means clustering algorithm ($K=3$)** profiles players into *Novice*, *Intermediate*, and *Expert* cohorts (Silhouette Score = $0.584$). A supervised **Decision Tree Classifier** predicts dynamic difficulty adjustments, resulting in an empirical **+26.7% boost in novice completion rates** and a **-24.1% reduction in frustration stalls**.

---
**Keywords**: Artificial Intelligence, Knowledge Representation, Forward Chaining, Heuristic Search ($A^*$), Constraint Satisfaction Problems (CSP), K-Means Clustering, Decision Tree, Dynamic Difficulty Adjustment.

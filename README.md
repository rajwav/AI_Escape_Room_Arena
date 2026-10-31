# 🎮 AI GAME ARENA: Multi-Game Intelligent Reasoning & Search Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bm-ai-escape-room-arena.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-45%2F45%20passing-brightgreen.svg)](Source_Code/tests/test_all.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 **LIVE DEPLOYMENT**: Experience the live playable arena directly in your browser:  
> 👉 **[https://bm-ai-escape-room-arena.streamlit.app/](https://bm-ai-escape-room-arena.streamlit.app/)**

---

> **NVIDIA Innovative Assignment — Subject: Artificial Intelligence & Machine Learning (AIML)**  
> **Project Title**: AI Escape Room & Multi-Game AI Reasoning Arena  
> **Core Concepts**: Knowledge Representation (Horn Clauses), Forward Chaining Inference, State-Space Search (BFS vs A*), Minimax Adversarial Search, Constraint Satisfaction (CSP Backtracking with MRV), Unsupervised Telemetry Clustering (K-Means $K=3$), Supervised Dynamic Difficulty Adjustment (Decision Tree Classifier), and Universal Deterministic Scoring.

---

## 🌟 Executive Overview
The **AI Game Arena** is an extensible multi-game intelligence platform featuring a dark, cinematic, futuristic UI. The platform demonstrates how symbolic artificial intelligence (logic rules, state-space planning, and adversarial game tree search) seamlessly unifies with empirical machine learning (cognitive telemetry profiling and adaptive pacing).

```
+=============================================================================================+
|                                      AI GAME ARENA PLATFORM                                 |
+=============================================================================================+
|                                                                                             |
|   1. 🔐 AI ESCAPE ROOM (Primary):  Forward Chaining + A* Heuristic Search + CSP Vault Locks |
|   2. 🧩 QUANTUM SUDOKU:            9×9 Constraint Satisfaction Problem + Backtracking MRV   |
|   3. 💣 QUANTUM MINESWEEPER:       9×9 Grid (10 Mines) • 8-Neighbor Logic • 1 Life Only     |
|   4. ❌⭕ TIC TAC TOE:              2-Player Local + Minimax Zero-Sum Game Tree Search       |
|   5. ♟️ QUANTUM CHESS:              8×8 Adversarial State-Space Search & Piece Heuristics   |
|                                                                                             |
|   Universal Deterministic Scoring:                                                          |
|       SCORE = max(0, 10000 - (elapsed_seconds × 10))                                        |
|                                                                                             |
+=============================================================================================+
```

---

## 🧩 AIML Syllabus & Algorithm Mapping

| Game | Primary AIML Concept | Implementation Details |
| :--- | :--- | :--- |
| **AI Escape Room** | Forward Chaining + A* Search + CSP + ML | Production rules ($P \implies Q$), Proof Tree, Admissible Heuristic $h(s)$, K-Means ($K=3$), Decision Tree DDA. |
| **Quantum Sudoku** | CSP Backtracking + MRV | 9×9 grid constraint propagation, Minimum Remaining Values variable selection, Candidate elimination. |
| **Quantum Minesweeper** | Propositional Logic & CSP Deduction | 9×9 grid with 10 hidden mines, 8-neighbor counts, flood-fill BFS, 1 Life only, 1 guaranteed initial hint. |
| **Tic Tac Toe** | Minimax Adversarial Search | Complete game-tree expansion, zero-sum utility function ($+10/-10$), depth-penalized evaluation. |
| **Quantum Chess** | State-Space Heuristic Search | 8×8 board representation, legal move generation, piece-square material evaluation. |
| **Player Adaptation** | ML Adaptive Difficulty | 6D telemetry vector, K-Means clustering (Silhouette: 0.584), Decision Tree classifier ($96.7\%$ accuracy). |

---

## 📁 Repository Structure

```text
Project_2_AI_Escape_Room/
├── README.md                           # Master Project Guide
├── Documentation/                      # Full 11-Part Academic Documentation Suite
│   ├── 01_Abstract.md
│   ├── 02_Problem_Statement.md
│   ├── 03_Objectives.md
│   ├── 04_Literature_Survey.md
│   ├── 05_System_Architecture.md
│   ├── 06_Algorithms_Mathematical_Model.md
│   ├── 07_Implementation_Details.md    # Viva Defense Q&A
│   ├── 08_Results_Visualizations.md
│   ├── 09_Evaluation_Metrics.md
│   ├── 10_Future_Scope_Limitations.md
│   └── 11_References.md
├── Source_Code/
│   ├── app.py                          # Main Game Arena Hub & Router
│   ├── games/                          # Modular UI Game Modules
│   │   ├── __init__.py
│   │   ├── escape_room.py              # Primary 3-Column Escape Room Game
│   │   ├── sudoku.py                   # 9×9 Sudoku CSP Game
│   │   ├── bomb_box.py                 # Bomb in the Box Logic Puzzle
│   │   ├── tic_tac_toe.py              # Tic Tac Toe + Minimax AI
│   │   └── chess.py                    # 8×8 Chess Game
│   ├── src/                            # Core AIML Algorithm Engines
│   │   ├── knowledge_base.py           # Propositional Ground Facts & Horn Clauses
│   │   ├── inference_engine.py         # Forward Chaining Production System & Proof Tree
│   │   ├── environment.py              # Facility GameState & Room Transition Physics
│   │   ├── search_algorithms.py        # BFS vs A* Heuristic Search Planner
│   │   ├── puzzle_engine.py            # Backtracking Vault Lock & Reagents CSP
│   │   ├── scoring_engine.py           # Universal Deterministic Scoring System
│   │   ├── sudoku_engine.py            # 9×9 Sudoku CSP & MRV Backtracking Solver
│   │   ├── bomb_engine.py              # Survival Deduction & Sensor Logic Engine
│   │   ├── ttt_engine.py               # Minimax Adversarial Game Tree Search
│   │   ├── chess_engine.py             # 8×8 Board Representation & Legal Moves
│   │   ├── adaptive_difficulty.py      # Telemetry, K-Means, Decision Tree DDA
│   │   ├── ml_evaluator.py             # Metrics Evaluator & 120-Player Experiment
│   │   └── visualizer.py               # ASCII Proof Trees & Benchmark Tables
│   ├── tests/                          # 45 Automated Unit Tests (100% Passing)
│   │   ├── test_inference.py
│   │   ├── test_search.py
│   │   ├── test_csp.py
│   │   ├── test_ml_module.py
│   │   ├── test_sudoku.py
│   │   ├── test_bomb_box.py
│   │   ├── test_tic_tac_toe.py
│   │   ├── test_chess.py
│   │   ├── test_scoring.py
│   │   └── test_all.py                 # Master Test Runner
│   └── requirements.txt
├── Dataset/                            # Exported Datasets
├── Models/                             # Exported ML JSON Models
├── Demo/
│   └── run_demo.sh                     # Bash Launcher
└── Screenshots/
```

---

## 🚀 Quickstart & Execution Guide

### 🌐 Live Cloud Deployment (No Setup Needed!)
Play directly on Streamlit Community Cloud:
👉 **[https://bm-ai-escape-room-arena.streamlit.app/](https://bm-ai-escape-room-arena.streamlit.app/)**

---

### 1. Run Automated Test Suite (45/45 Tests Passing)
```bash
python3 Source_Code/tests/test_all.py
```

### 2. Launch Interactive Game Arena Web Interface
```bash
streamlit run Source_Code/app.py
```

### 3. Launch Interactive Terminal CLI
```bash
python3 Source_Code/src/main.py
# Or via launcher:
./Demo/run_demo.sh
```

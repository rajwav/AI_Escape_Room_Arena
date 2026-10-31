"""
AI GAME ARENA: MULTI-GAME REASONING & SEARCH PLATFORM
Core Game: AI Escape Room
Additional Arena Games: Quantum Sudoku, Bomb in the Box, Tic Tac Toe, Quantum Chess
Demonstrating Knowledge Representation, A* Search, Minimax, CSP Backtracking, and ML Adaptive Difficulty.
"""

import streamlit as st
import time
import os
import sys

# Ensure src and games directories are in python path
root_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(root_dir, "src")
games_path = os.path.join(root_dir, "games")

for p in [root_dir, src_path, games_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

from games import (
    render_escape_room_game,
    render_sudoku_game,
    render_minesweeper_game,
    render_tic_tac_toe_game,
    render_chess_game
)
from environment import EscapeRoomEnvironment
from search_algorithms import EscapeRoomSearchPlanner
from puzzle_engine import EscapeRoomPuzzles
from adaptive_difficulty import (
    PlayerTelemetry, SyntheticTelemetryGenerator,
    KMeansClustering, DecisionTreeClassifier, AdaptiveDifficultyEngine
)
from ml_evaluator import MLEvaluator, AdaptiveDifficultyExperiment
from visualizer import EscapeRoomVisualizer

# --- Page Configuration ---
st.set_page_config(
    page_title="AI GAME ARENA | Multi-Game Intelligence Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Styling System ---
st.markdown("""
<style>
    /* Dark Theme & High-Tech Typography */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1527 0%, #050811 100%);
        color: #e2e8f0;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Top Command Header */
    .game-header {
        background: linear-gradient(90deg, rgba(0, 255, 204, 0.08) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(168, 85, 247, 0.08) 100%);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .game-title {
        font-family: 'Consolas', monospace;
        font-size: 2.0rem;
        font-weight: 900;
        letter-spacing: 3px;
        color: #00ffcc;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
        margin: 0;
    }
    .game-subtitle {
        font-size: 0.85rem;
        letter-spacing: 2px;
        color: #94a3b8;
        margin: 4px 0 0 0;
    }
    .system-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34d399;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }

    /* Glassmorphic Panels */
    .hud-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }
    .card-title {
        font-family: 'Consolas', monospace;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #38bdf8;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 6px;
    }

    /* Room Progression Nodes */
    .room-node {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.25s ease;
    }
    .room-node-active {
        background: linear-gradient(135deg, rgba(0, 255, 204, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1.5px solid #00ffcc;
        box-shadow: 0 0 16px rgba(0, 255, 204, 0.3);
    }
    .room-node-completed {
        border-color: #10b981;
        background: rgba(16, 185, 129, 0.08);
    }
    .room-node-locked {
        opacity: 0.55;
        border-color: #475569;
    }
    .room-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .room-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
    }

    /* Inventory Items */
    .inv-item-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #38bdf8;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .inv-item-name {
        font-weight: 700;
        color: #38bdf8;
        font-size: 0.9rem;
    }

    /* Fact Chips */
    .fact-chip {
        display: inline-block;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 3px 8px;
        margin: 3px 2px;
        font-family: 'Consolas', monospace;
        font-size: 0.75rem;
        color: #cbd5e1;
    }
    .fact-derived {
        border-color: #a855f7;
        background: rgba(168, 85, 247, 0.15);
        color: #e9d5ff;
        font-weight: 600;
    }
    .fact-observed {
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
        color: #bae6fd;
    }

    /* Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: #f8fafc;
        font-weight: 700;
        border-radius: 8px;
        padding: 10px 16px;
        transition: all 0.2s ease;
        text-align: left;
    }
    .stButton > button:hover {
        border-color: #00ffcc;
        box-shadow: 0 0 12px rgba(0, 255, 204, 0.3);
        color: #00ffcc;
        transform: translateY(-1px);
    }

    /* Feedback Banners */
    .feedback-success {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 14px 18px;
        color: #34d399;
        margin-bottom: 14px;
    }
    .feedback-info {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid #38bdf8;
        border-radius: 8px;
        padding: 14px 18px;
        color: #bae6fd;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- Top Header ---
st.markdown("""
<div class="game-header">
    <div>
        <h1 class="game-title">🎮 AI GAME ARENA</h1>
        <p class="game-subtitle">REASON • SEARCH • PLAY • ADAPT</p>
    </div>
    <div class="system-status-pill">
        <div class="pulse-dot"></div>
        ARENA PLATFORM ONLINE
    </div>
</div>
""", unsafe_allow_html=True)

# --- Arena Mode Navigation ---
with st.sidebar:
    st.markdown("### 🕹️ Arena Game Hub")
    selected_arena_mode = st.radio(
        "Select Active Game / Console:",
        [
            "🔐 1. AI Escape Room (Primary)",
            "🧩 2. Quantum Sudoku (CSP)",
            "💣 3. Quantum Minesweeper (Logic & Deduction)",
            "❌⭕ 4. Tic Tac Toe (Minimax)",
            "♟️ 5. Quantum Chess (Adversarial)"
        ]
    )


# --- ROUTER ---
if selected_arena_mode.startswith("🔐"):
    render_escape_room_game()

elif selected_arena_mode.startswith("🧩"):
    render_sudoku_game()

elif selected_arena_mode.startswith("💣"):
    render_minesweeper_game()

elif selected_arena_mode.startswith("❌⭕"):
    render_tic_tac_toe_game()

elif selected_arena_mode.startswith("♟️"):
    render_chess_game()

elif selected_arena_mode.startswith("🤖"):
    st.markdown("""
    <div class="hud-card">
        <div class="card-title">🤖 AUTONOMOUS SEARCH PLANNING ENGINE</div>
        <p style="color:#94a3b8; margin:0;">
            Compares <b>Uninformed Breadth-First Search (BFS)</b> with <b>Informed A* Heuristic Search</b> on state-space graph planning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    env = EscapeRoomEnvironment()
    planner = EscapeRoomSearchPlanner(env)

    if st.button("🚀 EXECUTE SEARCH ALGORITHM BENCHMARK", key="hub_search_bench_btn"):
        with st.spinner("Expanding state space nodes..."):
            bfs_res = planner.breadth_first_search()
            astar_res = planner.a_star_search()

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.metric("BFS Nodes Explored", bfs_res.nodes_explored)
            st.metric("BFS Execution Time", f"{bfs_res.execution_time_ms:.3f} ms")
        with col_b2:
            st.metric("A* Nodes Explored", astar_res.nodes_explored, delta=f"-{bfs_res.nodes_explored - astar_res.nodes_explored} nodes pruned")
            st.metric("A* Execution Time", f"{astar_res.execution_time_ms:.3f} ms")
        with col_b3:
            reduction = ((bfs_res.nodes_explored - astar_res.nodes_explored) / bfs_res.nodes_explored) * 100
            st.metric("Search Space Pruning", f"{reduction:.1f}%", delta="A* Heuristic Advantage")
            st.metric("Optimal Path Steps", astar_res.path_cost)

        st.subheader("📊 Search Benchmark Summary Table")
        st.text(EscapeRoomVisualizer.render_search_comparison_table(bfs_res.get_summary(), astar_res.get_summary()))

        st.subheader("🗺️ Optimal Action Plan (Generated by A*)")
        for step_idx, (act, st_node) in enumerate(astar_res.solution_path, 1):
            st.markdown(f"**Step {step_idx:02d}:** `{act}` *(Sector: {st_node.current_room})*")

        st.subheader("🔍 Complete Forward Chaining Deduction Proof Tree")
        reasoning_data = planner.generate_reasoning_trace(astar_res.solution_path)
        with st.expander("Inspect Step-by-Step Reasoning Trace", expanded=True):
            st.text(EscapeRoomVisualizer.render_reasoning_trace(reasoning_data))

elif selected_arena_mode.startswith("📈"):
    st.markdown("""
    <div class="hud-card">
        <div class="card-title">📈 MACHINE LEARNING ADAPTIVE PACING MODULE</div>
        <p style="color:#94a3b8; margin:0;">
            Demonstrates <b>K-Means Clustering</b> ($K=3$) for player skill profiling (Novice, Intermediate, Expert) and a <b>Decision Tree Classifier</b> for real-time Dynamic Difficulty Adjustment (DDA).
        </p>
    </div>
    """, unsafe_allow_html=True)

    dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=300, seed=42)
    feat_names = PlayerTelemetry.get_feature_names()
    X = [[d[k] for k in feat_names] for d in dataset]
    y_action = [d["recommended_difficulty"] for d in dataset]

    kmeans = KMeansClustering(k=3, random_state=42)
    kmeans.fit(X)
    sil_score = MLEvaluator.calculate_silhouette_score(X, kmeans.cluster_labels)

    split = int(0.8 * len(X))
    dt = DecisionTreeClassifier(max_depth=4)
    dt.fit(X[:split], y_action[:split])
    metrics = MLEvaluator.calculate_classification_metrics(y_action[split:], dt.predict(X[split:]))

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("K-Means Silhouette", f"{sil_score:.4f}", delta="Optimal Clusters")
    m2.metric("Decision Tree Accuracy", f"{metrics['accuracy']*100:.1f}%")
    m3.metric("Macro Precision", f"{metrics['macro_precision']:.4f}")
    m4.metric("Macro Recall", f"{metrics['macro_recall']:.4f}")
    m5.metric("Macro F1-Score", f"{metrics['macro_f1']:.4f}")

    st.subheader("🎯 Classification Confusion Matrix")
    st.text(EscapeRoomVisualizer.render_confusion_matrix(metrics))

elif selected_arena_mode.startswith("🧪"):
    st.markdown("""
    <div class="hud-card">
        <div class="card-title">🧪 120-PLAYER EMPIRICAL COHORT EXPERIMENT</div>
        <p style="color:#94a3b8; margin:0;">
            Comparative analysis simulating a 120-student cohort under <b>Fixed Static Difficulty</b> vs <b>ML-Based Adaptive Pacing</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    res = AdaptiveDifficultyExperiment.run_comparative_experiment(cohort_size=120, seed=42)
    imp = res["Empirical_Improvement"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Completion Rate Boost", f"+{imp['Completion_Rate_Boost_%']}%", delta="Adaptive Advantage")
    c2.metric("Time-To-Escape Reduction", f"-{imp['Time_To_Escape_Reduction_%']}%", delta="Faster Resolution")
    c3.metric("Frustration Drop Ratio", f"{imp['Frustration_Reduction_Ratio']}", delta="Fewer Stalls")

    st.subheader("📋 Detailed Cohort Experiment Telemetry")
    st.json(res)

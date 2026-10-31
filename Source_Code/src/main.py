"""
AI Escape Room - Main Application Entry Point
Unified command-line interface demonstrating:
1. Human Play Mode (Interactive Knowledge Reasoning)
2. AI Auto-Solver Mode (BFS vs A* Heuristic Search)
3. ML Module (K-Means Clustering, Decision Tree, Confusion Matrix, Silhouette)
4. Empirical Experiment (Fixed Static vs ML Adaptive Difficulty)
5. Comprehensive Test Runner
"""

import sys
import os
import json
import time

# Ensure src directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import EscapeRoomEnvironment, GameState
from knowledge_base import KnowledgeBase
from inference_engine import ForwardChainingEngine
from search_algorithms import EscapeRoomSearchPlanner
from puzzle_engine import EscapeRoomPuzzles
from adaptive_difficulty import (
    PlayerTelemetry, SyntheticTelemetryGenerator,
    KMeansClustering, DecisionTreeClassifier, AdaptiveDifficultyEngine
)
from ml_evaluator import MLEvaluator, AdaptiveDifficultyExperiment
from visualizer import EscapeRoomVisualizer


def run_human_mode():
    """Interactive human escape room exploration with live reasoning engine."""
    env = EscapeRoomEnvironment()
    state = env.get_initial_state()
    telemetry = PlayerTelemetry()
    start_time = time.time()

    # Pre-train adaptive ML assistant
    dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=200)
    feat_names = PlayerTelemetry.get_feature_names()
    X = [[d[k] for k in feat_names] for d in dataset]
    y = [d["recommended_difficulty"] for d in dataset]
    
    kmeans = KMeansClustering(k=3)
    kmeans.fit(X)
    dt = DecisionTreeClassifier(max_depth=4)
    dt.fit(X, y)
    adapter = AdaptiveDifficultyEngine(kmeans, dt)

    print("\n" + "=" * 65)
    print("      WELCOME TO AI ESCAPE ROOM: THE DEDUCTIVE LABYRINTH      ")
    print("=" * 65)
    print("Goal: Navigate rooms, discover clues, solve puzzles, and activate the Escape Portal.")

    while not env.is_goal_state(state):
        telemetry.time_spent_seconds = time.time() - start_time
        print(EscapeRoomVisualizer.render_map(state.current_room))
        print(f"Current Room:   {state.current_room}")
        print(f"Inventory:      {list(state.inventory) if state.inventory else '[Empty]'}")
        print(f"Known Facts:    {len(state.world_facts)} total asserted/inferred facts")

        # Check ML adaptive intervention
        if telemetry.total_actions > 2:
            eval_res = adapter.evaluate_player(telemetry)
            if eval_res["recommended_action"] == "Assist":
                print(f"\n[AI Adaptive Assistant - {eval_res['skill_archetype']} Detected]")
                print(f"  --> {eval_res['dynamic_guidance']}")

        successors = env.get_successors(state)
        print("\nAvailable Actions:")
        for idx, (action_name, next_s, _) in enumerate(successors, 1):
            print(f"  {idx}. {action_name}")
        print(f"  H. Request Deductive Hint (Logs telemetry)")
        print(f"  P. View Current Deduction Proof Tree")
        print(f"  Q. Quit to Main Menu")

        choice = input("\nEnter choice: ").strip()

        if choice.lower() == 'q':
            print("Exiting to menu...")
            return
        elif choice.lower() == 'h':
            telemetry.log_hint()
            print("\n[HINT ENGINE] Inferred knowledge from facts:")
            for f in state.world_facts:
                if f.startswith("revealed") or f.startswith("synthesized") or f.startswith("known"):
                    print(f"  - {f}")
            input("\nPress Enter to continue...")
            continue
        elif choice.lower() == 'p':
            derived, steps = env._evaluate_inference(set(state.world_facts))
            print(EscapeRoomVisualizer.render_proof_tree(steps))
            input("\nPress Enter to continue...")
            continue

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(successors):
                action_name, next_state, _ = successors[choice_idx]
                telemetry.log_action(action_name, valid=True, room=next_state.current_room)
                state = next_state
                print(f"\n>>> Executed: {action_name}")
            else:
                telemetry.log_action("invalid", valid=False, room=state.current_room)
                print("Invalid action index.")
        except ValueError:
            telemetry.log_action("invalid", valid=False, room=state.current_room)
            print("Invalid input.")

    print("\n" + "=" * 65)
    print("  CONGRATULATIONS! YOU HAVE SUCCESSFULLY ESCAPED THE FACILITY! ")
    print("=" * 65)
    print(f"Total Actions Taken:   {telemetry.total_actions}")
    print(f"Total Time Spent:      {round(time.time() - start_time, 2)} seconds")
    print(f"Invalid Attempts:      {telemetry.invalid_actions}")
    input("\nPress Enter to return to menu...")


def run_ai_solver_mode():
    """Runs automated BFS vs A* search algorithms with benchmarking."""
    env = EscapeRoomEnvironment()
    planner = EscapeRoomSearchPlanner(env)

    print("\n" + "=" * 65)
    print("         AI AUTONOMOUS ESCAPE ROOM SEARCH SOLVER             ")
    print("=" * 65)
    print("Running Uninformed Search (BFS) and Informed Search (A*)...")

    bfs_res = planner.breadth_first_search()
    astar_res = planner.a_star_search()

    print("\n" + EscapeRoomVisualizer.render_search_comparison_table(
        bfs_res.get_summary(), astar_res.get_summary()
    ))

    print("\n--- OPTIMAL SOLUTION ACTION PLAN (Generated by A*) ---")
    for step_num, (action, st) in enumerate(astar_res.solution_path, 1):
        print(f"  Step {step_num:02d}: {action:<35} | Room: {st.current_room}")

    # Generate complete Knowledge Base & Forward Chaining Reasoning Trace
    reasoning_data = planner.generate_reasoning_trace(astar_res.solution_path)
    
    print("\n--- STEP-BY-STEP REASONING & KNOWLEDGE DERIVATION ---")
    print(EscapeRoomVisualizer.render_reasoning_trace(reasoning_data))

    print("\n--- COMPLETE FORWARD CHAINING DEDUCTION PROOF TREE ---")
    print(EscapeRoomVisualizer.render_proof_tree(reasoning_data["proof_tree_steps"]))

    input("\nPress Enter to return to menu...")


def run_ml_training_evaluation():
    """Trains K-Means and Decision Tree models, evaluates metrics and saves artifacts."""
    print("\n" + "=" * 65)
    print("         ML ADAPTIVE DIFFICULTY: TRAINING & EVALUATION        ")
    print("=" * 65)

    dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "Dataset", "player_telemetry.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "Models")
    os.makedirs(models_dir, exist_ok=True)

    print(f"1. Generating synthetic player telemetry dataset (N=300)...")
    dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=300, seed=42)
    SyntheticTelemetryGenerator.save_to_csv(dataset, dataset_path)
    print(f"   [OK] Dataset saved to: {dataset_path}")

    feat_names = PlayerTelemetry.get_feature_names()
    X = [[d[k] for k in feat_names] for d in dataset]
    y_true_skill = [d["skill_cluster"] for d in dataset]
    y_true_action = [d["recommended_difficulty"] for d in dataset]

    print("\n2. Training K-Means Unsupervised Clustering (K=3)...")
    kmeans = KMeansClustering(k=3, random_state=42)
    kmeans.fit(X)
    sil_score = MLEvaluator.calculate_silhouette_score(X, kmeans.cluster_labels)
    print(f"   - Centroids Converged: {len(kmeans.centroids)} clusters")
    print(f"   - Clustering Inertia:  {round(kmeans.inertia_, 2)}")
    print(f"   - Silhouette Score:    {sil_score} (Good separation > 0.50)")

    print("\n3. Training Supervised Decision Tree Classifier...")
    # Train / Test split (80/20)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y_true_action[:split_idx], y_true_action[split_idx:]

    dt = DecisionTreeClassifier(max_depth=4)
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)

    metrics = MLEvaluator.calculate_classification_metrics(y_test, y_pred)
    print("\n--- CLASSIFICATION EVALUATION METRICS (Test Set N=60) ---")
    print(f"  * Accuracy:           {metrics['accuracy'] * 100:.2f}%")
    print(f"  * Macro Precision:    {metrics['macro_precision']:.4f}")
    print(f"  * Macro Recall:       {metrics['macro_recall']:.4f}")
    print(f"  * Macro F1-Score:     {metrics['macro_f1']:.4f}")
    print(f"  * Weighted F1-Score:  {metrics['weighted_f1']:.4f}")

    print("\n" + EscapeRoomVisualizer.render_confusion_matrix(metrics))

    # Save trained models
    kmeans_model_path = os.path.join(models_dir, "kmeans_player_model.json")
    with open(kmeans_model_path, "w") as f:
        json.dump({
            "k": kmeans.k,
            "centroids": kmeans.centroids,
            "cluster_names": kmeans.cluster_names,
            "silhouette_score": sil_score,
            "inertia": kmeans.inertia_
        }, f, indent=2)

    dt_model_path = os.path.join(models_dir, "decision_tree_model.json")
    with open(dt_model_path, "w") as f:
        json.dump({
            "classes": dt.classes,
            "max_depth": dt.max_depth,
            "test_accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"]
        }, f, indent=2)

    print(f"\n[OK] Models successfully exported to: {models_dir}")
    input("\nPress Enter to return to menu...")


def run_adaptive_experiment():
    """Runs the Fixed vs Adaptive Difficulty empirical experiment."""
    print("\n" + "=" * 65)
    print("    EXPERIMENT: FIXED DIFFICULTY vs ML ADAPTIVE DIFFICULTY    ")
    print("=" * 65)
    print("Simulating a cohort of 120 players under both regimes...\n")

    res = AdaptiveDifficultyExperiment.run_comparative_experiment(cohort_size=120, seed=42)

    fixed = res["Fixed_Difficulty"]
    adapt = res["ML_Adaptive_Difficulty"]
    imp = res["Empirical_Improvement"]

    header = f"{'Experiment Metric':<30} | {'Fixed Difficulty':<20} | {'ML Adaptive Difficulty':<22}"
    sep = "-" * 78
    
    rows = [
        f"{'Cohort Size':<30} | {str(res['Cohort_Size']):<20} | {str(res['Cohort_Size']):<22}",
        f"{'Escape Completion Rate':<30} | {str(fixed['Completion_Rate_%']) + '%' :<20} | {str(adapt['Completion_Rate_%']) + '%':<22}",
        f"{'Frustrated / Stalled Players':<30} | {str(fixed['Stalled_Frustrated_Players']):<20} | {str(adapt['Stalled_Frustrated_Players']):<22}",
        f"{'Average Escape Time (sec)':<30} | {str(fixed['Average_Escape_Time_Sec']) + 's':<20} | {str(adapt['Average_Escape_Time_Sec']) + 's':<22}",
        f"{'Total Hints Consumed':<30} | {str(fixed['Total_Hints_Consumed']):<20} | {str(adapt['Total_Hints_Consumed']):<22}"
    ]

    print("\n".join([sep, header, sep] + rows + [sep]))
    print(f"\n[Key Research Finding]")
    print(f"  1. Completion Rate Boost:       +{imp['Completion_Rate_Boost_%']}%")
    print(f"  2. Time-To-Escape Reduction:     -{imp['Time_To_Escape_Reduction_%']}%")
    print(f"  3. Frustration Reduction Ratio:  {imp['Frustration_Reduction_Ratio']} players")

    input("\nPress Enter to return to menu...")


def main():
    while True:
        print("\n" + "=" * 65)
        print("  AI ESCAPE ROOM: KNOWLEDGE REASONING & SEARCH SYSTEM (AIML)  ")
        print("=" * 65)
        print("  1. Play Escape Room (Human Interactive Mode)")
        print("  2. Run AI Search Solver (BFS vs A* Benchmark & Proof Tree)")
        print("  3. Train & Evaluate ML Module (K-Means, Decision Tree, F1, Silhouette)")
        print("  4. Run Comparative Experiment (Fixed vs ML Adaptive Difficulty)")
        print("  5. Run CSP Constraint Lock Solver Demonstration")
        print("  6. Exit")
        print("=" * 65)

        choice = input("Enter choice (1-6): ").strip()
        if choice == '1':
            run_human_mode()
        elif choice == '2':
            run_ai_solver_mode()
        elif choice == '3':
            run_ml_training_evaluation()
        elif choice == '4':
            run_adaptive_experiment()
        elif choice == '5':
            print("\n--- CSP BACKTRACKING SOLVER DEMO ---")
            vault_sol = EscapeRoomPuzzles.solve_vault_lock(clues_unlocked=True)
            print(f"1. Vault Lock (D1, D2, D3 in 1..9, Sum=15, Ascending, D2 is Prime, D3=2*D1+1):")
            print(f"   => Solution Found: {vault_sol}")
            chem_sol = EscapeRoomPuzzles.solve_chemical_reagent_puzzle()
            print(f"\n2. Chemical Synthesis (Reagent A, B, C in 1..5, Total=9ml, 2*A=B, C>A):")
            print(f"   => Solution Found: {chem_sol}")
            input("\nPress Enter to return to menu...")
        elif choice == '6':
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid selection. Please enter a number 1-6.")


if __name__ == "__main__":
    main()

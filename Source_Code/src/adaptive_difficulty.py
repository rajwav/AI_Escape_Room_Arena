"""
AI Escape Room - ML-Based Adaptive Difficulty Module
Implements:
1. Real-time Player Telemetry Collection
2. Synthetic Telemetry Dataset Generation
3. K-Means Clustering (Unsupervised Player Skill Profiling: Novice, Intermediate, Expert)
4. Decision Tree Classifier (Supervised Difficulty Prediction: Assist, Standard, Challenge)
5. Dynamic Difficulty Engine (Feedback loop into Knowledge Base & Search Engine)
"""

import math
import random
import csv
import json
import os
from typing import List, Dict, Tuple, Any, Optional


class PlayerTelemetry:
    """Tracks gameplay metrics for real-time and offline ML analysis."""
    def __init__(self):
        self.time_spent_seconds: float = 0.0
        self.total_actions: int = 0
        self.invalid_actions: int = 0
        self.hint_requests: int = 0
        self.rooms_visited: List[str] = ["Foyer"]
        self.backtracks: int = 0
        self.csp_attempts: int = 0
        self.optimal_steps: int = 13  # Known theoretical minimum steps

    def log_action(self, action: str, valid: bool, room: str):
        self.total_actions += 1
        if not valid:
            self.invalid_actions += 1
        
        if len(self.rooms_visited) > 0 and room != self.rooms_visited[-1]:
            if room in self.rooms_visited[:-1]:
                self.backtracks += 1
            self.rooms_visited.append(room)

    def log_hint(self):
        self.hint_requests += 1

    def log_csp_attempt(self):
        self.csp_attempts += 1

    def get_feature_vector(self) -> List[float]:
        """
        Extracts 6 normalized numerical features:
        [time_per_room, hint_count, invalid_actions, backtrack_rate, search_efficiency, csp_attempts]
        """
        unique_rooms = max(1, len(set(self.rooms_visited)))
        time_per_room = self.time_spent_seconds / unique_rooms
        backtrack_rate = self.backtracks / max(1, len(self.rooms_visited))
        search_efficiency = min(1.0, self.optimal_steps / max(1, self.total_actions))
        
        return [
            round(time_per_room, 2),
            float(self.hint_requests),
            float(self.invalid_actions),
            round(backtrack_rate, 3),
            round(search_efficiency, 3),
            float(self.csp_attempts)
        ]

    @staticmethod
    def get_feature_names() -> List[str]:
        return [
            "time_per_room",
            "hint_requests",
            "invalid_actions",
            "backtrack_rate",
            "search_efficiency",
            "csp_attempts"
        ]


class SyntheticTelemetryGenerator:
    """
    Generates synthetic telemetry datasets modeling realistic player distributions:
    - Novice: High time, frequent hints, high mistakes, low search efficiency.
    - Intermediate: Moderate time, occasional hints, few mistakes, balanced exploration.
    - Expert: Rapid completion, 0 hints, minimal mistakes, near-optimal efficiency.
    """
    @staticmethod
    def generate_dataset(num_samples: int = 300, seed: int = 42) -> List[Dict[str, Any]]:
        random.seed(seed)
        samples = []
        
        archetypes = [
            ("Novice", "Assist", 0.40),       # 40% of cohort
            ("Intermediate", "Standard", 0.35), # 35% of cohort
            ("Expert", "Challenge", 0.25)       # 25% of cohort
        ]

        for i in range(num_samples):
            r = random.random()
            if r < 0.40:
                skill, target_action, _ = archetypes[0]
                time_per_room = random.gauss(65.0, 12.0)
                hints = max(1, int(random.gauss(4.5, 1.2)))
                invalid_acts = max(2, int(random.gauss(5.0, 1.5)))
                backtrack_rate = min(1.0, max(0.2, random.gauss(0.45, 0.1)))
                efficiency = min(0.6, max(0.15, random.gauss(0.35, 0.08)))
                csp_attempts = max(2, int(random.gauss(4.0, 1.0)))
            elif r < 0.75:
                skill, target_action, _ = archetypes[1]
                time_per_room = random.gauss(35.0, 8.0)
                hints = max(0, int(random.gauss(1.5, 0.8)))
                invalid_acts = max(0, int(random.gauss(1.8, 0.9)))
                backtrack_rate = min(0.4, max(0.05, random.gauss(0.22, 0.06)))
                efficiency = min(0.85, max(0.55, random.gauss(0.68, 0.08)))
                csp_attempts = max(1, int(random.gauss(2.0, 0.7)))
            else:
                skill, target_action, _ = archetypes[2]
                time_per_room = random.gauss(14.0, 4.0)
                hints = 0 if random.random() > 0.1 else 1
                invalid_acts = max(0, int(random.gauss(0.3, 0.5)))
                backtrack_rate = min(0.15, max(0.0, random.gauss(0.06, 0.04)))
                efficiency = min(1.0, max(0.80, random.gauss(0.92, 0.05)))
                csp_attempts = 1

            samples.append({
                "player_id": f"P_{i+1:04d}",
                "time_per_room": round(max(5.0, time_per_room), 2),
                "hint_requests": hints,
                "invalid_actions": invalid_acts,
                "backtrack_rate": round(max(0.0, backtrack_rate), 3),
                "search_efficiency": round(max(0.05, efficiency), 3),
                "csp_attempts": csp_attempts,
                "skill_cluster": skill,
                "recommended_difficulty": target_action
            })

        return samples

    @staticmethod
    def save_to_csv(samples: List[Dict[str, Any]], filepath: str):
        if not samples:
            return
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        keys = list(samples[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(samples)


class KMeansClustering:
    """
    K-Means Clustering from First Principles for Semester-Level Explainability.
    Groups player feature vectors into K distinct clusters.
    """
    def __init__(self, k: int = 3, max_iters: int = 100, random_state: int = 42):
        self.k = k
        self.max_iters = max_iters
        self.random_state = random_state
        self.centroids: List[List[float]] = []
        self.cluster_labels: List[int] = []
        self.inertia_: float = 0.0
        self.cluster_names: Dict[int, str] = {}

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def fit(self, X: List[List[float]]):
        random.seed(self.random_state)
        n_samples = len(X)
        n_features = len(X[0])

        # Initialize centroids randomly from data
        initial_indices = random.sample(range(n_samples), self.k)
        self.centroids = [list(X[idx]) for idx in initial_indices]

        for _ in range(self.max_iters):
            # Assignment step
            labels = []
            for point in X:
                distances = [self._euclidean_distance(point, c) for c in self.centroids]
                labels.append(distances.index(min(distances)))

            # Update step
            new_centroids = []
            for cluster_idx in range(self.k):
                cluster_points = [X[i] for i in range(n_samples) if labels[i] == cluster_idx]
                if cluster_points:
                    mean_point = [
                        sum(p[dim] for p in cluster_points) / len(cluster_points)
                        for dim in range(n_features)
                    ]
                    new_centroids.append(mean_point)
                else:
                    new_centroids.append(self.centroids[cluster_idx])

            # Check convergence
            shifts = sum(self._euclidean_distance(c1, c2) for c1, c2 in zip(self.centroids, new_centroids))
            self.centroids = new_centroids
            if shifts < 1e-4:
                break

        self.cluster_labels = labels
        # Compute Inertia (Sum of squared errors)
        self.inertia_ = sum(
            self._euclidean_distance(X[i], self.centroids[labels[i]]) ** 2
            for i in range(n_samples)
        )

        # Label cluster names by skill based on average search_efficiency (feature index 4)
        efficiency_ranks = sorted(
            range(self.k),
            key=lambda c_idx: self.centroids[c_idx][4]
        )
        self.cluster_names[efficiency_ranks[0]] = "Novice / Casual"
        self.cluster_names[efficiency_ranks[1]] = "Intermediate"
        self.cluster_names[efficiency_ranks[2]] = "Expert / Speedrunner"

    def predict(self, point: List[float]) -> int:
        distances = [self._euclidean_distance(point, c) for c in self.centroids]
        return distances.index(min(distances))

    def get_cluster_name(self, cluster_idx: int) -> str:
        return self.cluster_names.get(cluster_idx, f"Cluster {cluster_idx}")


class DecisionTreeNode:
    """Node in the Decision Tree Classifier."""
    def __init__(
        self,
        feature_idx: Optional[int] = None,
        threshold: Optional[float] = None,
        left: Optional['DecisionTreeNode'] = None,
        right: Optional['DecisionTreeNode'] = None,
        value: Optional[str] = None
    ):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # Leaf class label

    @property
    def is_leaf(self) -> bool:
        return self.value is not None


class DecisionTreeClassifier:
    """
    Decision Tree Classifier from First Principles using Gini Impurity.
    Used to predict dynamic difficulty adaptation: Assist vs Standard vs Challenge.
    """
    def __init__(self, max_depth: int = 4, min_samples_split: int = 5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root: Optional[DecisionTreeNode] = None
        self.classes: List[str] = []

    @staticmethod
    def _gini_impurity(y: List[str]) -> float:
        if not y:
            return 0.0
        total = len(y)
        counts = {}
        for item in y:
            counts[item] = counts.get(item, 0) + 1
        return 1.0 - sum((cnt / total) ** 2 for cnt in counts.values())

    def fit(self, X: List[List[float]], y: List[str]):
        self.classes = sorted(list(set(y)))
        self.root = self._grow_tree(X, y, depth=0)

    def _grow_tree(self, X: List[List[float]], y: List[str], depth: int) -> DecisionTreeNode:
        num_samples = len(y)
        num_classes = len(set(y))

        # Base stopping conditions
        if depth >= self.max_depth or num_classes <= 1 or num_samples < self.min_samples_split:
            most_common = max(set(y), key=y.count)
            return DecisionTreeNode(value=most_common)

        # Find best split
        best_feat, best_thresh = None, None
        best_gain = -1.0
        current_gini = self._gini_impurity(y)
        n_features = len(X[0])

        for feat in range(n_features):
            values = sorted(list(set(X[i][feat] for i in range(num_samples))))
            for i in range(len(values) - 1):
                thresh = (values[i] + values[i + 1]) / 2.0
                left_y = [y[j] for j in range(num_samples) if X[j][feat] <= thresh]
                right_y = [y[j] for j in range(num_samples) if X[j][feat] > thresh]

                if not left_y or not right_y:
                    continue

                p_left = len(left_y) / num_samples
                p_right = len(right_y) / num_samples
                gini_split = p_left * self._gini_impurity(left_y) + p_right * self._gini_impurity(right_y)
                gain = current_gini - gini_split

                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = thresh

        if best_gain <= 1e-5 or best_feat is None:
            most_common = max(set(y), key=y.count)
            return DecisionTreeNode(value=most_common)

        # Split data
        left_idx = [i for i in range(num_samples) if X[i][best_feat] <= best_thresh]
        right_idx = [i for i in range(num_samples) if X[i][best_feat] > best_thresh]

        left_node = self._grow_tree([X[i] for i in left_idx], [y[i] for i in left_idx], depth + 1)
        right_node = self._grow_tree([X[i] for i in right_idx], [y[i] for i in right_idx], depth + 1)

        return DecisionTreeNode(
            feature_idx=best_feat,
            threshold=best_thresh,
            left=left_node,
            right=right_node
        )

    def predict_one(self, x: List[float]) -> str:
        node = self.root
        while not node.is_leaf:
            if x[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.value

    def predict(self, X: List[List[float]]) -> List[str]:
        return [self.predict_one(x) for x in X]


class AdaptiveDifficultyEngine:
    """
    Coordinates real-time gameplay feedback and adapts escape room assistance.
    """
    def __init__(self, kmeans_model: KMeansClustering, dt_model: DecisionTreeClassifier):
        self.kmeans = kmeans_model
        self.dt = dt_model

    def evaluate_player(self, telemetry: PlayerTelemetry) -> Dict[str, Any]:
        vec = telemetry.get_feature_vector()
        cluster_idx = self.kmeans.predict(vec)
        skill_archetype = self.kmeans.get_cluster_name(cluster_idx)
        recommendation = self.dt.predict_one(vec)

        # Dynamic Game Interventions
        if recommendation == "Assist":
            guidance = "PROACTIVE HINT: The UV torch reveals invisible ink on ancient parchment. Check the Library cabinet."
            extra_clues = True
        elif recommendation == "Challenge":
            guidance = "CHALLENGE ACTIVE: Redundant room clues masked. Maximum search efficiency required."
            extra_clues = False
        else:
            guidance = "STANDARD PACING: Regular puzzle hints available on request."
            extra_clues = True

        return {
            "player_features": vec,
            "cluster_index": cluster_idx,
            "skill_archetype": skill_archetype,
            "recommended_action": recommendation,
            "dynamic_guidance": guidance,
            "extra_clues_enabled": extra_clues
        }

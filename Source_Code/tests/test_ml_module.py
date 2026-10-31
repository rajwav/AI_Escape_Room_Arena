"""
Unit Tests for Machine Learning Adaptive Difficulty Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adaptive_difficulty import (
    PlayerTelemetry, SyntheticTelemetryGenerator,
    KMeansClustering, DecisionTreeClassifier
)
from ml_evaluator import MLEvaluator


class TestMLModule(unittest.TestCase):
    def test_synthetic_telemetry_generation(self):
        dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=50, seed=10)
        self.assertEqual(len(dataset), 50)
        self.assertIn("time_per_room", dataset[0])
        self.assertIn("skill_cluster", dataset[0])

    def test_kmeans_clustering_convergence(self):
        dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=90, seed=42)
        feat_keys = PlayerTelemetry.get_feature_names()
        X = [[d[k] for k in feat_keys] for d in dataset]

        kmeans = KMeansClustering(k=3, random_state=42)
        kmeans.fit(X)

        self.assertEqual(len(kmeans.centroids), 3)
        self.assertEqual(len(kmeans.cluster_labels), 90)

        # Silhouette score should be positive and indicative of good clustering
        sil = MLEvaluator.calculate_silhouette_score(X, kmeans.cluster_labels)
        self.assertGreater(sil, 0.40)

    def test_decision_tree_classifier_accuracy(self):
        dataset = SyntheticTelemetryGenerator.generate_dataset(num_samples=150, seed=42)
        feat_keys = PlayerTelemetry.get_feature_names()
        X = [[d[k] for k in feat_keys] for d in dataset]
        y = [d["recommended_difficulty"] for d in dataset]

        # 80/20 split
        X_train, X_test = X[:120], X[120:]
        y_train, y_test = y[:120], y[120:]

        dt = DecisionTreeClassifier(max_depth=4)
        dt.fit(X_train, y_train)
        y_pred = dt.predict(X_test)

        metrics = MLEvaluator.calculate_classification_metrics(y_test, y_pred)
        # Should achieve high classification accuracy (> 85%) on synthetic distribution
        self.assertGreater(metrics["accuracy"], 0.85)
        self.assertGreater(metrics["macro_f1"], 0.80)


if __name__ == "__main__":
    unittest.main()

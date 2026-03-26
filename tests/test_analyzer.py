import numpy as np
import pandas as pd
import pytest

from experiment.metrics.analyzer import AnalysisResults, paired_token_test, run_analysis


class TestPairedTokenTest:
    def test_known_difference(self):
        """Paired t-test with known mean difference."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "condition": [
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                ],
                "total_tokens": [1000, 800, 1200, 900, 1100, 850],
            }
        )
        mean_diff, p_value, cohens_d, ci_lower, ci_upper = paired_token_test(df)

        assert mean_diff > 0
        assert isinstance(p_value, float)
        assert isinstance(cohens_d, float)
        assert ci_lower < ci_upper

    def test_identical_data(self):
        """Identical control/treatment should yield mean_diff near zero."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "condition": [
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                ],
                "total_tokens": [1000, 1000, 1200, 1200, 1100, 1100],
            }
        )
        mean_diff, p_value, cohens_d, ci_lower, ci_upper = paired_token_test(df)

        assert abs(mean_diff) < 1e-10
        assert p_value > 0.99

    def test_missing_condition_raises(self):
        """Should raise ValueError if only one condition present."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t2"],
                "condition": ["control", "control"],
                "total_tokens": [1000, 1200],
            }
        )
        with pytest.raises(ValueError, match="both.*control.*treatment"):
            paired_token_test(df)

    def test_no_paired_data_raises(self):
        """Should raise ValueError if no task_ids overlap."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t2"],
                "condition": ["control", "treatment"],
                "total_tokens": [1000, 1200],
            }
        )
        with pytest.raises(ValueError, match="No paired data"):
            paired_token_test(df)

    def test_bootstrap_ci_contains_mean(self):
        """Bootstrap CI should contain the sample mean difference."""
        np.random.seed(42)
        n = 30
        control = np.random.normal(1000, 100, n)
        treatment = control - 150 + np.random.normal(0, 50, n)

        task_ids = [f"t{i}" for i in range(n)]
        df = pd.DataFrame(
            {
                "task_id": task_ids * 2,
                "condition": ["control"] * n + ["treatment"] * n,
                "total_tokens": list(control) + list(treatment),
            }
        )
        mean_diff, p_value, cohens_d, ci_lower, ci_upper = paired_token_test(df)

        assert ci_lower <= mean_diff <= ci_upper
        assert cohens_d > 0.5

    def test_large_effect_size(self):
        """Large known difference should produce Cohen's d > 0.8."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t1", "t2", "t2", "t3", "t3", "t4", "t4", "t5", "t5"],
                "condition": ["control", "treatment"] * 5,
                "total_tokens": [
                    1000,
                    200,
                    1100,
                    250,
                    1050,
                    220,
                    1200,
                    300,
                    950,
                    180,
                ],
            }
        )
        mean_diff, p_value, cohens_d, ci_lower, ci_upper = paired_token_test(df)

        assert cohens_d > 0.8
        assert p_value < 0.05


class TestRunAnalysis:
    def test_returns_analysis_results(self, tmp_path):
        """run_analysis should return AnalysisResults dataclass."""
        df = pd.DataFrame(
            {
                "task_id": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "condition": [
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                    "control",
                    "treatment",
                ],
                "total_tokens": [1000, 800, 1200, 900, 1100, 850],
            }
        )
        csv_path = tmp_path / "results.csv"
        df.to_csv(csv_path, index=False)

        results = run_analysis(csv_path)

        assert isinstance(results, AnalysisResults)
        assert results.mean_diff > 0
        assert isinstance(results.p_value, float)
        assert isinstance(results.cohens_d, float)
        assert results.ci_lower < results.ci_upper

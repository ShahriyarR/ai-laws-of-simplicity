from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class AnalysisResults:
    """Results from paired t-test analysis."""

    mean_diff: float
    t_stat: float
    p_value: float
    cohens_d: float
    ci_lower: float
    ci_upper: float


def load_results(csv_path: Path) -> pd.DataFrame:
    """Load results from CSV."""
    return pd.read_csv(csv_path)


def paired_token_test(df: pd.DataFrame) -> tuple[float, float, float, float, float]:
    """Run paired t-test for token reduction.

    Returns:
        Tuple of (mean_diff, p_value, cohens_d, ci_lower, ci_upper)
    """
    pivot = df.pivot_table(
        index="task_id", columns="condition", values="total_tokens", aggfunc="first"
    )

    if "control" not in pivot.columns or "treatment" not in pivot.columns:
        raise ValueError("Data must contain both 'control' and 'treatment' conditions")

    pivot = pivot.dropna(subset=["control", "treatment"])

    if len(pivot) == 0:
        raise ValueError(
            "No paired data found - each task needs both control and treatment runs"
        )

    control = pivot["control"].values
    treatment = pivot["treatment"].values

    t_stat, p_value = stats.ttest_rel(control, treatment)

    mean_diff = (control - treatment).mean()
    pooled_std = np.sqrt((control.std() ** 2 + treatment.std() ** 2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

    if np.isnan(p_value):
        p_value = 1.0

    diffs = control - treatment
    n_bootstrap = 10000
    rng = np.random.default_rng(42)
    bootstrap_samples = rng.choice(diffs, size=(n_bootstrap, len(diffs)), replace=True)
    bootstrap_means = bootstrap_samples.mean(axis=1)
    ci_lower = float(np.percentile(bootstrap_means, 2.5))
    ci_upper = float(np.percentile(bootstrap_means, 97.5))

    return mean_diff, p_value, cohens_d, ci_lower, ci_upper


def run_analysis(results_csv: Path) -> AnalysisResults:
    """Run statistical analysis on experiment results.

    Args:
        results_csv: Path to CSV with columns: task_id, condition, total_tokens

    Returns:
        AnalysisResults with paired t-test statistics
    """
    df = load_results(results_csv)

    mean_diff, p_value, cohens_d, ci_lower, ci_upper = paired_token_test(df)

    control = df[df["condition"] == "control"]["total_tokens"]
    treatment = df[df["condition"] == "treatment"]["total_tokens"]

    pivot = df.pivot_table(
        index="task_id", columns="condition", values="total_tokens", aggfunc="first"
    ).dropna()

    t_stat, _ = stats.ttest_rel(pivot["control"].values, pivot["treatment"].values)

    return AnalysisResults(
        mean_diff=mean_diff,
        t_stat=float(t_stat),
        p_value=p_value,
        cohens_d=cohens_d,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
    )

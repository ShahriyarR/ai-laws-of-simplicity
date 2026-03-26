#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiment.config import DEFAULT_CONFIG
from experiment.runner import ExperimentRunner


def main():
    """Analyze existing results without re-running experiments."""
    runner = ExperimentRunner(DEFAULT_CONFIG)

    results_csv = runner.config.results_dir / "aggregate_results.csv"
    if not results_csv.exists():
        print(f"Error: No results found at {results_csv}")
        print("Run the experiment first: uv run python -m experiment")
        sys.exit(1)

    analysis = runner.analyze()

    print("=== Analysis Summary ===")
    print(f"  Mean token diff (control - treatment): {analysis['mean_diff']:+.0f}")
    print(f"  t-statistic: {analysis['t_stat']:.3f}")
    print(f"  p-value: {analysis['p_value']:.4f}")
    print(f"  Cohen's d: {analysis['cohens_d']:.3f}")
    print(f"  95% CI: [{analysis['ci_95'][0]:.0f}, {analysis['ci_95'][1]:.0f}]")

    generate_figures(runner.config.results_dir)

    print("Analysis complete. See:")
    print(f"  - {runner.config.results_dir / 'analysis.json'}")
    print(f"  - {runner.config.results_dir / 'figures/'}")


def generate_figures(output_dir: Path) -> None:
    """Generate paper figures."""
    import pandas as pd
    import matplotlib.pyplot as plt

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    df = pd.read_csv(output_dir / "aggregate_results.csv")

    fig, ax = plt.subplots(figsize=(10, 6))
    control = df[df["condition"] == "control"]["total_tokens"]
    treatment = df[df["condition"] == "treatment"]["total_tokens"]

    ax.hist(control, bins=30, alpha=0.6, label="Control", color="blue")
    ax.hist(treatment, bins=30, alpha=0.6, label="Treatment", color="green")
    ax.axvline(
        control.mean(),
        color="blue",
        linestyle="--",
        label=f"Control mean: {control.mean():.0f}",
    )
    ax.axvline(
        treatment.mean(),
        color="green",
        linestyle="--",
        label=f"Treatment mean: {treatment.mean():.0f}",
    )
    ax.set_xlabel("Total Tokens")
    ax.set_ylabel("Frequency")
    ax.set_title("Token Distribution: Control vs Treatment")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "figure1_token_distribution.png", dpi=150)
    plt.close()

    print(f"Figures saved to {figures_dir}")


if __name__ == "__main__":
    main()

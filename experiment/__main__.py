import argparse
import json

from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(
        description="Run Laws of Simplicity A/B experiment"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-3-5-sonnet-20241022",
        help="LiteLLM model string",
    )
    parser.add_argument(
        "--benchmarks",
        type=str,
        nargs="+",
        default=["swe_bench_lite"],
        choices=["swe_bench_lite"],
        help="Benchmarks to run (currently only swe_bench_lite)",
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=100,
        help="Number of tasks to run",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds per task",
    )

    args = parser.parse_args()

    config = ExperimentConfig(
        benchmarks=args.benchmarks,
        num_tasks_per_benchmark=args.num_tasks,
        model_string=args.model,
        temperature=args.temperature,
        timeout_seconds=args.timeout,
    )

    runner = ExperimentRunner(config)
    runner.run()
    analysis = runner.analyze()

    print("\n=== Analysis Summary ===")
    print(f"  Mean token diff (control - treatment): {analysis['mean_diff']:+.0f}")
    print(f"  t-statistic: {analysis['t_stat']:.3f}")
    print(f"  p-value: {analysis['p_value']:.4f}")
    print(f"  Cohen's d: {analysis['cohens_d']:.3f}")
    print(f"  95% CI: [{analysis['ci_95'][0]:.0f}, {analysis['ci_95'][1]:.0f}]")

    with open(runner.config.results_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nFull analysis saved to {runner.config.results_dir / 'analysis.json'}")


if __name__ == "__main__":
    main()

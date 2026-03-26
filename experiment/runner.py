import json
from pathlib import Path
from typing import Any

from experiment.config import ExperimentConfig, DEFAULT_CONFIG
from experiment.harness.base import TaskSpec
from experiment.harness.swe_bench import SWEBenchHarness
from experiment.metrics.collector import MetricsCollector
from experiment.mini_agent.runner import MiniAgentRunner


class ExperimentRunner:
    """Orchestrates A/B experiments using mini-swe-agent."""

    def __init__(self, config: ExperimentConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self.config.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.config.results_dir.mkdir(parents=True, exist_ok=True)

        self.collector = MetricsCollector(self.config.raw_data_dir)
        self.harness = SWEBenchHarness()
        self.runner = MiniAgentRunner(
            model_name=self.config.model_string,
            step_limit=self.config.step_limit,
            cost_limit=self.config.cost_limit,
            temperature=self.config.temperature,
            output_dir=self.config.raw_data_dir,
        )
        self.task_metadata: dict[str, dict[str, Any]] = {}

    def run(self) -> None:
        """Run the full experiment."""
        print(f"Starting experiment:")
        print(f"  Model: {self.config.model_string}")
        print(f"  Tasks: {self.config.num_tasks_per_benchmark}")
        print(f"  Step limit: {self.config.step_limit}")
        print(f"  Cost limit: ${self.config.cost_limit}")

        tasks = self.harness.load_tasks(
            self.config.num_tasks_per_benchmark,
            self.config.random_seed,
        )
        print(f"Loaded {len(tasks)} tasks")

        for task in tasks:
            self.task_metadata[task.task_id] = {
                "benchmark": task.benchmark,
                "difficulty": task.difficulty,
            }

        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Task: {task.task_id}")
            self._run_task(task)

        print("\n=== Aggregating results ===")
        self.collector.to_csv(self.config.results_dir / "aggregate_results.csv")

        with open(self.config.results_dir / "task_metadata.json", "w") as f:
            json.dump(self.task_metadata, f, indent=2)

        print(f"Results saved to {self.config.results_dir}")

    def _run_task(self, task: TaskSpec) -> None:
        """Run a single task in both conditions."""
        if hash(task.task_id) % 2 == 0:
            conditions = ["control", "treatment"]
        else:
            conditions = ["treatment", "control"]

        for condition in conditions:
            print(f"  Running {condition}...")

            skills = (
                self.config.treatment_skills
                if condition == "treatment"
                else self.config.control_skills
            )
            ctx = self.runner.create_fresh_context(skills=skills)

            metrics_ctx = self.collector.start_run(
                task.task_id,
                task.benchmark,
                condition,
            )

            try:
                result = self.runner.run_agent(
                    ctx,
                    task.prompt,
                    timeout=self.config.timeout_seconds,
                )

                self.collector.update_tokens(
                    metrics_ctx,
                    result["input_tokens"],
                    result["output_tokens"],
                )
                for _ in range(result["iterations"]):
                    self.collector.increment_iteration(metrics_ctx)

                self.collector.end_run(metrics_ctx, success=True)

            except Exception as e:
                print(f"  ERROR: {e}")
                self.collector.end_run(metrics_ctx, success=False, error=str(e))

            finally:
                self.runner.cleanup(ctx)

    def analyze(self) -> dict[str, Any]:
        """Run statistical analysis on collected results."""
        from experiment.metrics.analyzer import run_analysis

        results_csv = self.config.results_dir / "aggregate_results.csv"
        results = run_analysis(results_csv)

        return {
            "mean_diff": results.mean_diff,
            "t_stat": results.t_stat,
            "p_value": results.p_value,
            "cohens_d": results.cohens_d,
            "ci_95": [results.ci_lower, results.ci_upper],
        }

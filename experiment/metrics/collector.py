import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class RunMetrics:
    """Collected metrics for a single agent run."""

    task_id: str
    benchmark: str
    condition: str

    # Primary metrics
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Secondary metrics
    success: bool
    time_seconds: float
    iterations: int

    # Metadata
    error: str | None
    timestamp: str

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)


class MetricsCollector:
    """Collects and stores experiment metrics."""

    def __init__(self, output_dir: Path):
        """Initialize collector.

        Args:
            output_dir: Directory to store JSON logs
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_run(self, task_id: str, benchmark: str, condition: str) -> dict[str, Any]:
        """Start a new run, return context for tracking.

        Returns:
            Context dict with start_time
        """
        return {
            "task_id": task_id,
            "benchmark": benchmark,
            "condition": condition,
            "start_time": time.time(),
            "start_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "iterations": 0,
            "input_tokens": 0,
            "output_tokens": 0,
        }

    def update_tokens(self, ctx: dict, input_tokens: int, output_tokens: int) -> None:
        """Update token counts in context."""
        ctx["input_tokens"] += input_tokens
        ctx["output_tokens"] += output_tokens

    def increment_iteration(self, ctx: dict) -> None:
        """Increment iteration count."""
        ctx["iterations"] += 1

    def end_run(
        self,
        ctx: dict,
        success: bool,
        error: str | None = None,
    ) -> RunMetrics:
        """End run and return final metrics.

        Args:
            ctx: Run context from start_run
            success: Whether task succeeded
            error: Error message if failed

        Returns:
            Final RunMetrics object
        """
        end_time = time.time()

        metrics = RunMetrics(
            task_id=ctx["task_id"],
            benchmark=ctx["benchmark"],
            condition=ctx["condition"],
            input_tokens=ctx["input_tokens"],
            output_tokens=ctx["output_tokens"],
            total_tokens=ctx["input_tokens"] + ctx["output_tokens"],
            success=success,
            time_seconds=end_time - ctx["start_time"],
            iterations=ctx["iterations"],
            error=error,
            timestamp=ctx["start_timestamp"],
        )

        # Save to JSON (sanitize task_id for filename safety)
        safe_task_id = ctx["task_id"].replace("/", "_").replace(":", "_")
        output_file = self.output_dir / f"{safe_task_id}_{ctx['condition']}.json"
        with open(output_file, "w") as f:
            json.dump(metrics.to_json(), f, indent=2)

        return metrics

    def load_all_results(self) -> list[RunMetrics]:
        """Load all results from output directory."""
        results = []
        for json_file in self.output_dir.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
                results.append(RunMetrics(**data))
        return results

    def to_csv(self, output_path: Path) -> None:
        """Export all results to CSV."""
        import pandas as pd

        results = self.load_all_results()
        df = pd.DataFrame([r.to_json() for r in results])
        df.to_csv(output_path, index=False)

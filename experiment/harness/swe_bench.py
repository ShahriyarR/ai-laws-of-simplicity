import random
from pathlib import Path
from typing import Any

from .base import BenchmarkHarness, TaskSpec


class SWEBenchHarness(BenchmarkHarness):
    """Harness for SWE-bench Lite benchmark."""

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path
        self._tasks_cache: dict[str, TaskSpec] | None = None

    def _load_dataset(self) -> list[dict[str, Any]]:
        """Load SWE-bench Lite dataset."""
        from datasets import load_dataset

        dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
        return [item for item in dataset]

    def load_tasks(self, num_tasks: int, seed: int) -> list[TaskSpec]:
        """Load a random sample of SWE-bench tasks.

        Difficulty classification based on patch line count:
        - Simple: <10 lines changed
        - Medium: 10-50 lines changed
        - Complex: >50 lines changed
        """
        all_tasks = self._load_dataset()

        rng = random.Random(seed)
        sampled = rng.sample(all_tasks, min(num_tasks, len(all_tasks)))

        task_specs = []
        for task in sampled:
            patch = task.get("patch", "")
            lines_changed = len(patch.split("\n")) if patch else 0

            if lines_changed < 10:
                difficulty = "simple"
            elif lines_changed <= 50:
                difficulty = "medium"
            else:
                difficulty = "complex"

            spec = TaskSpec(
                task_id=task["instance_id"],
                benchmark="swe_bench_lite",
                prompt=task["problem_statement"],
                test_file=None,
                expected_solution=task.get("patch"),
                difficulty=difficulty,
                repo=task.get("repo", ""),
                base_commit=task.get("base_commit"),
                problem_statement=task["problem_statement"],
            )
            task_specs.append(spec)

        self._tasks_cache = {t.task_id: t for t in task_specs}
        return task_specs

    def get_task_metadata(self, task_id: str) -> dict[str, Any]:
        """Get SWE-bench task metadata."""
        if self._tasks_cache and task_id in self._tasks_cache:
            task = self._tasks_cache[task_id]
            return {
                "difficulty": task.difficulty,
                "repo": task.repo,
                "base_commit": task.base_commit,
            }
        return {}

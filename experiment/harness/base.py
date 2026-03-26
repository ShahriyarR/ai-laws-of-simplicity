from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TaskSpec:
    """Specification for a benchmark task."""

    task_id: str
    benchmark: str
    prompt: str
    test_file: str | None
    expected_solution: str | None
    difficulty: str  # "simple", "medium", "complex"

    # SWE-bench specific
    repo: str | None = None
    base_commit: str | None = None
    problem_statement: str | None = None


class BenchmarkHarness(ABC):
    """Abstract base class for benchmark harnesses."""

    @abstractmethod
    def load_tasks(self, num_tasks: int, seed: int) -> list[TaskSpec]:
        """Load a random sample of tasks from the benchmark.

        Args:
            num_tasks: Number of tasks to sample
            seed: Random seed for reproducibility

        Returns:
            List of TaskSpec objects
        """
        pass

    @abstractmethod
    def get_task_metadata(self, task_id: str) -> dict[str, Any]:
        """Get metadata for a specific task.

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with task metadata (difficulty, repo, etc.)
        """
        pass

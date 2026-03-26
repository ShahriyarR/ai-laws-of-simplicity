from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for A/B experiment measuring impact of Laws of Simplicity skill.

    Sample sizes based on G*Power: d=0.3, alpha=0.05, power=0.80 requires n=90.
    """

    benchmarks: list[str] = field(default_factory=lambda: ["swe_bench_lite"])
    num_tasks_per_benchmark: int = 100

    model_string: str = "anthropic/claude-3-5-sonnet-20241022"
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout_seconds: int = 600

    step_limit: int = 50
    cost_limit: float = 3.0

    conditions: tuple[str, str] = ("control", "treatment")

    control_skills: list[Path] = field(default_factory=list)
    treatment_skills: list[Path] = field(
        default_factory=lambda: [Path("skills/laws-of-simplicity/SKILL.md")]
    )

    raw_data_dir: Path = Path("data/raw")
    results_dir: Path = Path("data/results")

    random_seed: int = 42
    counterbalance: bool = True

    required_sample_size: int = 90
    planned_sample_size: int = 100


DEFAULT_CONFIG = ExperimentConfig()

import json
from pathlib import Path
from typing import Any


_DEFAULT_PARSED_RESULT = {
    "input_tokens": 0,
    "output_tokens": 0,
    "num_turns": 0,
    "cost": 0.0,
    "exit_status": "not_found",
    "patch": "",
}


def parse_run_result(result: dict[str, Any]) -> dict[str, Any]:
    """Parse mini-swe-agent run result into experiment metrics.

    Args:
        result: Dict returned by DefaultAgent.run()

    Returns:
        Dict with standardized metrics:
        - input_tokens: Total input tokens across all turns
        - output_tokens: Total output tokens across all turns
        - num_turns: Number of agent steps taken
        - cost: Total USD cost
        - exit_status: How agent stopped (submitted/step_limit/cost_limit/error)
        - patch: Generated patch text (if any)
    """
    info = result.get("info", {})
    model_stats = info.get("model_stats", {})

    return {
        "input_tokens": model_stats.get("tokens_sent", 0),
        "output_tokens": model_stats.get("tokens_received", 0),
        "num_turns": model_stats.get("api_calls", 0),
        "cost": model_stats.get("instance_cost", 0.0),
        "exit_status": info.get("exit_status", "unknown"),
        "patch": info.get("submission", ""),
    }


def parse_serialized_trajectory(trajectory_path: str) -> dict[str, Any]:
    """Parse a saved trajectory JSON file.

    Args:
        trajectory_path: Path to saved trajectory JSON

    Returns:
        Same format as parse_run_result
    """
    path = Path(trajectory_path)
    if not path.exists():
        return _DEFAULT_PARSED_RESULT.copy()

    with open(path) as f:
        data = json.load(f)

    return parse_run_result(data)

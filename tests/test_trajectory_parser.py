import json
from pathlib import Path

import pytest

from experiment.mini_agent.trajectory_parser import (
    parse_run_result,
    parse_serialized_trajectory,
)


def test_parse_run_result_complete():
    """Test parsing a complete run result with all fields."""
    result = {
        "info": {
            "model_stats": {
                "tokens_sent": 1500,
                "tokens_received": 500,
                "api_calls": 10,
                "instance_cost": 0.025,
            },
            "exit_status": "submitted",
            "submission": "diff --git a/file.py b/file.py\n...",
        }
    }

    parsed = parse_run_result(result)

    assert parsed["input_tokens"] == 1500
    assert parsed["output_tokens"] == 500
    assert parsed["num_turns"] == 10
    assert parsed["cost"] == 0.025
    assert parsed["exit_status"] == "submitted"
    assert parsed["patch"] == "diff --git a/file.py b/file.py\n..."


def test_parse_run_result_minimal():
    """Test parsing run result with missing optional fields."""
    result = {
        "info": {
            "model_stats": {},
            "exit_status": "step_limit",
        }
    }

    parsed = parse_run_result(result)

    assert parsed["input_tokens"] == 0
    assert parsed["output_tokens"] == 0
    assert parsed["num_turns"] == 0
    assert parsed["cost"] == 0.0
    assert parsed["exit_status"] == "step_limit"
    assert parsed["patch"] == ""


def test_parse_run_result_empty():
    """Test parsing completely empty result."""
    result = {}

    parsed = parse_run_result(result)

    assert parsed["input_tokens"] == 0
    assert parsed["output_tokens"] == 0
    assert parsed["num_turns"] == 0
    assert parsed["cost"] == 0.0
    assert parsed["exit_status"] == "unknown"
    assert parsed["patch"] == ""


def test_parse_run_result_partial_model_stats():
    """Test parsing with partial model_stats."""
    result = {
        "info": {
            "model_stats": {
                "tokens_sent": 1000,
                "api_calls": 5,
            },
            "exit_status": "cost_limit",
        }
    }

    parsed = parse_run_result(result)

    assert parsed["input_tokens"] == 1000
    assert parsed["output_tokens"] == 0
    assert parsed["num_turns"] == 5
    assert parsed["cost"] == 0.0
    assert parsed["exit_status"] == "cost_limit"


def test_parse_run_result_error_exit():
    """Test parsing result with error exit status."""
    result = {
        "info": {
            "model_stats": {
                "tokens_sent": 300,
                "tokens_received": 100,
                "api_calls": 3,
                "instance_cost": 0.005,
            },
            "exit_status": "error",
        }
    }

    parsed = parse_run_result(result)

    assert parsed["exit_status"] == "error"
    assert parsed["input_tokens"] == 300
    assert parsed["output_tokens"] == 100


def test_parse_serialized_trajectory_success(tmp_path):
    """Test parsing a saved trajectory JSON file."""
    trajectory_data = {
        "info": {
            "model_stats": {
                "tokens_sent": 2000,
                "tokens_received": 800,
                "api_calls": 15,
                "instance_cost": 0.04,
            },
            "exit_status": "submitted",
            "submission": "patch content here",
        }
    }

    trajectory_file = tmp_path / "trajectory.json"
    trajectory_file.write_text(json.dumps(trajectory_data))

    parsed = parse_serialized_trajectory(str(trajectory_file))

    assert parsed["input_tokens"] == 2000
    assert parsed["output_tokens"] == 800
    assert parsed["num_turns"] == 15
    assert parsed["cost"] == 0.04
    assert parsed["exit_status"] == "submitted"
    assert parsed["patch"] == "patch content here"


def test_parse_serialized_trajectory_missing_file(tmp_path):
    """Test parsing non-existent trajectory file."""
    nonexistent = tmp_path / "does_not_exist.json"

    parsed = parse_serialized_trajectory(str(nonexistent))

    assert parsed["input_tokens"] == 0
    assert parsed["output_tokens"] == 0
    assert parsed["num_turns"] == 0
    assert parsed["cost"] == 0.0
    assert parsed["exit_status"] == "not_found"
    assert parsed["patch"] == ""


def test_parse_serialized_trajectory_empty_file(tmp_path):
    """Test parsing empty trajectory file."""
    trajectory_file = tmp_path / "empty.json"
    trajectory_file.write_text("{}")

    parsed = parse_serialized_trajectory(str(trajectory_file))

    assert parsed["input_tokens"] == 0
    assert parsed["exit_status"] == "unknown"


def test_parse_serialized_trajectory_minimal(tmp_path):
    """Test parsing trajectory with minimal data."""
    trajectory_data = {
        "info": {
            "exit_status": "step_limit",
        }
    }

    trajectory_file = tmp_path / "minimal.json"
    trajectory_file.write_text(json.dumps(trajectory_data))

    parsed = parse_serialized_trajectory(str(trajectory_file))

    assert parsed["exit_status"] == "step_limit"
    assert parsed["input_tokens"] == 0
    assert parsed["output_tokens"] == 0


def test_parse_run_result_zero_cost():
    """Test that zero cost is preserved, not treated as missing."""
    result = {
        "info": {
            "model_stats": {
                "instance_cost": 0.0,
            },
        }
    }

    parsed = parse_run_result(result)

    assert parsed["cost"] == 0.0


def test_parse_run_result_empty_patch():
    """Test that empty string patch is preserved."""
    result = {
        "info": {
            "submission": "",
            "exit_status": "submitted",
        }
    }

    parsed = parse_run_result(result)

    assert parsed["patch"] == ""
    assert parsed["exit_status"] == "submitted"


def test_parsed_result_structure():
    """Test that parsed result has all expected keys."""
    result = {}
    parsed = parse_run_result(result)

    expected_keys = {
        "input_tokens",
        "output_tokens",
        "num_turns",
        "cost",
        "exit_status",
        "patch",
    }

    assert set(parsed.keys()) == expected_keys


def test_parse_run_result_types():
    """Test that parsed values have correct types."""
    result = {
        "info": {
            "model_stats": {
                "tokens_sent": 100,
                "tokens_received": 50,
                "api_calls": 3,
                "instance_cost": 0.01,
            },
            "exit_status": "submitted",
            "submission": "patch",
        }
    }

    parsed = parse_run_result(result)

    assert isinstance(parsed["input_tokens"], int)
    assert isinstance(parsed["output_tokens"], int)
    assert isinstance(parsed["num_turns"], int)
    assert isinstance(parsed["cost"], float)
    assert isinstance(parsed["exit_status"], str)
    assert isinstance(parsed["patch"], str)

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from experiment.mini_agent.runner import MiniAgentRunner


@pytest.fixture
def runner():
    """Create a MiniAgentRunner instance for testing."""
    return MiniAgentRunner(
        model_name="anthropic/claude-3-5-sonnet-20241022",
        step_limit=50,
        cost_limit=3.0,
        temperature=0.0,
    )


@pytest.fixture
def runner_with_output_dir(tmp_path):
    """Create a MiniAgentRunner with output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return MiniAgentRunner(
        model_name="test/model",
        output_dir=output_dir,
    )


def test_runner_init():
    """Test MiniAgentRunner initialization."""
    runner = MiniAgentRunner(
        model_name="test/model",
        step_limit=100,
        cost_limit=5.0,
        temperature=0.7,
    )

    assert runner.model_name == "test/model"
    assert runner.step_limit == 100
    assert runner.cost_limit == 5.0
    assert runner.temperature == 0.7
    assert runner.output_dir is None


def test_runner_init_with_output_dir(tmp_path):
    """Test MiniAgentRunner initialization with output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    runner = MiniAgentRunner(
        model_name="test/model",
        output_dir=output_dir,
    )

    assert runner.output_dir == output_dir


def test_create_fresh_context_control(runner):
    """Test create_fresh_context without skills (control)."""
    ctx = runner.create_fresh_context(skills=None)

    assert "config" in ctx
    assert "skill_content" in ctx
    assert ctx["skill_content"] == ""

    config = ctx["config"]
    assert config["model"]["model_name"] == "anthropic/claude-3-5-sonnet-20241022"
    assert config["agent"]["step_limit"] == 50
    assert config["agent"]["cost_limit"] == 3.0
    assert config["model"]["model_kwargs"]["temperature"] == 0.0
    assert "---" not in config["agent"]["system_template"]


def test_create_fresh_context_empty_skills_list(runner):
    """Test create_fresh_context with empty skills list."""
    ctx = runner.create_fresh_context(skills=[])

    assert ctx["skill_content"] == ""
    assert "---" not in ctx["config"]["agent"]["system_template"]


def test_create_fresh_context_treatment(runner, tmp_path):
    """Test create_fresh_context with skills (treatment)."""
    skill_file = tmp_path / "test-skill.md"
    skill_file.write_text("# Test Skill\n\nFollow these rules.")

    ctx = runner.create_fresh_context(skills=[skill_file])

    assert "config" in ctx
    assert "skill_content" in ctx
    assert ctx["skill_content"] == "loaded"

    config = ctx["config"]
    system_template = config["agent"]["system_template"]
    assert "# Test Skill" in system_template
    assert "Follow these rules." in system_template
    assert "\n\n---\n\n" in system_template


def test_create_fresh_context_multiple_skills(runner, tmp_path):
    """Test create_fresh_context with multiple skills (only first is used)."""
    skill1 = tmp_path / "skill1.md"
    skill1.write_text("First skill")
    skill2 = tmp_path / "skill2.md"
    skill2.write_text("Second skill")

    ctx = runner.create_fresh_context(skills=[skill1, skill2])

    system_template = ctx["config"]["agent"]["system_template"]
    assert "First skill" in system_template
    assert "Second skill" not in system_template


def test_run_agent_success(runner):
    """Test run_agent successful execution."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {"temperature": 0.0},
            },
            "agent": {
                "system_template": "Test system",
                "instance_template": "Test instance",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {
                "tokens_sent": 1000,
                "tokens_received": 500,
                "api_calls": 5,
                "instance_cost": 0.02,
            },
            "exit_status": "submitted",
            "submission": "diff --git a/test.py",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel") as MockModel,
        patch("minisweagent.environments.local.LocalEnvironment") as MockEnv,
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        result = runner.run_agent(ctx, "Test task", timeout=600)

    assert result["input_tokens"] == 1000
    assert result["output_tokens"] == 500
    assert result["output"] == "diff --git a/test.py"
    assert result["iterations"] == 5
    assert result["num_turns"] == 5
    assert result["return_code"] == 0
    assert result["cost"] == 0.02
    assert result["exit_status"] == "submitted"
    assert result["time_seconds"] > 0

    mock_agent_instance.run.assert_called_once_with(task="Test task")


def test_run_agent_step_limit(runner):
    """Test run_agent when step limit is reached."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {},
            },
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 10,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {
                "tokens_sent": 2000,
                "tokens_received": 800,
                "api_calls": 10,
                "instance_cost": 0.05,
            },
            "exit_status": "step_limit",
            "submission": "",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        result = runner.run_agent(ctx, "Test task")

    assert result["exit_status"] == "step_limit"
    assert result["return_code"] == 1
    assert result["output"] == ""


def test_run_agent_error_handling(runner):
    """Test run_agent error handling."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {},
            },
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.side_effect = RuntimeError("Test error")

        result = runner.run_agent(ctx, "Test task")

    assert result["exit_status"] == "error"
    assert result["return_code"] == 1
    assert result["input_tokens"] == 0
    assert result["output_tokens"] == 0
    assert result["output"] == ""
    assert result["iterations"] == 0
    assert result["num_turns"] == 0
    assert result["cost"] == 0.0
    assert "error" in result
    assert "Test error" in result["error"]


def test_run_agent_saves_trajectory(runner_with_output_dir):
    """Test run_agent saves trajectory when output_dir is set."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {},
            },
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {
                "tokens_sent": 100,
                "tokens_received": 50,
                "api_calls": 1,
                "instance_cost": 0.001,
            },
            "exit_status": "submitted",
            "submission": "patch",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        runner_with_output_dir.run_agent(ctx, "Test task")

        mock_agent_instance.save.assert_called_once()
        save_path = mock_agent_instance.save.call_args[0][0]
        assert save_path.parent == runner_with_output_dir.output_dir / "trajectories"
        assert save_path.suffix == ".json"


def test_run_agent_no_save_without_output_dir(runner):
    """Test run_agent doesn't save when output_dir is None."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {},
            },
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {},
            "exit_status": "submitted",
            "submission": "patch",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        runner.run_agent(ctx, "Test task")

        mock_agent_instance.save.assert_not_called()


def test_cleanup(runner):
    """Test cleanup is a no-op."""
    ctx = {"config": {}}

    runner.cleanup(ctx)


def test_run_agent_timeout_parameter(runner):
    """Test that timeout parameter is accepted (but not used by mini-swe-agent)."""
    ctx = {
        "config": {
            "model": {"model_name": "test/model", "model_kwargs": {}},
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {},
            "exit_status": "submitted",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        runner.run_agent(ctx, "Test task", timeout=300)


def test_run_agent_max_tokens_parameter(runner):
    """Test that max_tokens parameter is accepted (but unused)."""
    ctx = {
        "config": {
            "model": {"model_name": "test/model", "model_kwargs": {}},
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {},
            "exit_status": "submitted",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        runner.run_agent(ctx, "Test task", max_tokens=8000)


def test_run_agent_creates_correct_agent_config(runner):
    """Test that run_agent creates DefaultAgent with correct parameters."""
    ctx = {
        "config": {
            "model": {
                "model_name": "test/model",
                "model_kwargs": {"temperature": 0.5},
            },
            "agent": {
                "system_template": "Custom system",
                "instance_template": "Custom instance",
                "step_limit": 75,
                "cost_limit": 2.5,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {},
            "exit_status": "submitted",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel") as MockModel,
        patch("minisweagent.environments.local.LocalEnvironment") as MockEnv,
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        runner.run_agent(ctx, "Test task")

        MockAgent.assert_called_once()
        call_kwargs = MockAgent.call_args.kwargs
        assert call_kwargs["system_template"] == "Custom system"
        assert call_kwargs["instance_template"] == "Custom instance"
        assert call_kwargs["step_limit"] == 75
        assert call_kwargs["cost_limit"] == 2.5


def test_run_agent_timing(runner):
    """Test that run_agent accurately tracks time."""
    ctx = {
        "config": {
            "model": {"model_name": "test/model", "model_kwargs": {}},
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {},
            "exit_status": "submitted",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
        patch("time.time") as mock_time,
    ):
        mock_time.side_effect = [100.0, 105.5]

        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        result = runner.run_agent(ctx, "Test task")

        assert result["time_seconds"] == 5.5


def test_result_structure_complete(runner):
    """Test that run_agent result has all required fields."""
    ctx = {
        "config": {
            "model": {"model_name": "test/model", "model_kwargs": {}},
            "agent": {
                "system_template": "Test",
                "instance_template": "Test",
                "step_limit": 50,
                "cost_limit": 3.0,
            },
        }
    }

    mock_result = {
        "info": {
            "model_stats": {
                "tokens_sent": 100,
                "tokens_received": 50,
                "api_calls": 2,
                "instance_cost": 0.005,
            },
            "exit_status": "submitted",
            "submission": "patch content",
        }
    }

    with (
        patch("minisweagent.agents.default.DefaultAgent") as MockAgent,
        patch("minisweagent.models.litellm_model.LitellmModel"),
        patch("minisweagent.environments.local.LocalEnvironment"),
    ):
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.run.return_value = mock_result
        mock_agent_instance.serialize.return_value = mock_result

        result = runner.run_agent(ctx, "Test task")

        expected_keys = {
            "input_tokens",
            "output_tokens",
            "output",
            "iterations",
            "return_code",
            "time_seconds",
            "num_turns",
            "cost",
            "exit_status",
        }

        assert set(result.keys()) == expected_keys

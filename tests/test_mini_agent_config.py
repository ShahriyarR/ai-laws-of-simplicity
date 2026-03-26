from pathlib import Path

import pytest

from experiment.mini_agent.config_builder import (
    BASE_INSTANCE_TEMPLATE,
    BASE_SYSTEM_TEMPLATE,
    build_config,
    build_control_config,
    build_treatment_config,
)


def test_build_config_minimal():
    """Test build_config with minimal arguments."""
    config = build_config("anthropic/claude-3-5-sonnet-20241022")

    assert "agent" in config
    assert "environment" in config
    assert "model" in config

    assert config["agent"]["system_template"] == BASE_SYSTEM_TEMPLATE
    assert config["agent"]["instance_template"] == BASE_INSTANCE_TEMPLATE
    assert config["agent"]["step_limit"] == 50
    assert config["agent"]["cost_limit"] == 3.0

    assert config["environment"]["cwd"] == "/testbed"
    assert config["environment"]["timeout"] == 60
    assert config["environment"]["interpreter"] == ["bash", "-c"]
    assert config["environment"]["environment_class"] == "docker"

    assert config["model"]["model_name"] == "anthropic/claude-3-5-sonnet-20241022"
    assert config["model"]["model_kwargs"]["temperature"] == 0.0
    assert config["model"]["model_kwargs"]["drop_params"] is True


def test_build_config_with_custom_params():
    """Test build_config with custom parameters."""
    config = build_config(
        "openai/gpt-4",
        skill_content=None,
        step_limit=100,
        cost_limit=5.0,
        temperature=0.7,
        timeout=120,
    )

    assert config["agent"]["step_limit"] == 100
    assert config["agent"]["cost_limit"] == 5.0
    assert config["model"]["model_kwargs"]["temperature"] == 0.7
    assert config["environment"]["timeout"] == 120


def test_build_config_with_skill():
    """Test build_config with skill content."""
    skill_text = "# Test Skill\n\nAlways write clean code."
    config = build_config(
        "anthropic/claude-3-5-sonnet-20241022", skill_content=skill_text
    )

    expected_system = skill_text.strip() + "\n\n---\n\n" + BASE_SYSTEM_TEMPLATE
    assert config["agent"]["system_template"] == expected_system


def test_build_config_skill_prepending():
    """Test that skill content is prepended with separator."""
    skill_text = "Skill instructions here"
    config = build_config("test/model", skill_content=skill_text)

    system_template = config["agent"]["system_template"]
    assert system_template.startswith("Skill instructions here")
    assert "\n\n---\n\n" in system_template
    assert system_template.endswith(BASE_SYSTEM_TEMPLATE)


def test_build_config_environment_vars():
    """Test environment variables are set correctly."""
    config = build_config("test/model")

    env = config["environment"]["env"]
    assert env["PAGER"] == "cat"
    assert env["MANPAGER"] == "cat"
    assert env["LESS"] == "-R"
    assert env["PIP_PROGRESS_BAR"] == "off"
    assert env["TQDM_DISABLE"] == "1"


def test_build_control_config():
    """Test build_control_config creates config without skill."""
    config = build_control_config("anthropic/claude-3-5-sonnet-20241022")

    assert config["agent"]["system_template"] == BASE_SYSTEM_TEMPLATE
    assert "---" not in config["agent"]["system_template"]


def test_build_control_config_with_params():
    """Test build_control_config passes through parameters."""
    config = build_control_config(
        "test/model", step_limit=200, cost_limit=10.0, temperature=0.5
    )

    assert config["agent"]["step_limit"] == 200
    assert config["agent"]["cost_limit"] == 10.0
    assert config["model"]["model_kwargs"]["temperature"] == 0.5
    assert config["agent"]["system_template"] == BASE_SYSTEM_TEMPLATE


def test_build_treatment_config(tmp_path):
    """Test build_treatment_config loads skill from file."""
    skill_file = tmp_path / "test-skill.md"
    skill_file.write_text("# Test Skill\n\nFollow these rules.")

    config = build_treatment_config("anthropic/claude-3-5-sonnet-20241022", skill_file)

    system_template = config["agent"]["system_template"]
    assert "# Test Skill" in system_template
    assert "Follow these rules." in system_template
    assert "\n\n---\n\n" in system_template
    assert BASE_SYSTEM_TEMPLATE in system_template


def test_build_treatment_config_with_params(tmp_path):
    """Test build_treatment_config passes through parameters."""
    skill_file = tmp_path / "skill.md"
    skill_file.write_text("Skill content")

    config = build_treatment_config(
        "test/model", skill_file, step_limit=75, cost_limit=2.5, temperature=0.3
    )

    assert config["agent"]["step_limit"] == 75
    assert config["agent"]["cost_limit"] == 2.5
    assert config["model"]["model_kwargs"]["temperature"] == 0.3
    assert "Skill content" in config["agent"]["system_template"]


def test_config_structure_consistency():
    """Test control and treatment configs have same structure."""
    skill_file = (
        Path(__file__).parent.parent / "skills" / "laws-of-simplicity" / "SKILL.md"
    )

    if not skill_file.exists():
        pytest.skip(f"Skill file not found: {skill_file}")

    control = build_control_config("test/model")
    treatment = build_treatment_config("test/model", skill_file)

    assert control.keys() == treatment.keys()
    assert control["agent"].keys() == treatment["agent"].keys()
    assert control["environment"] == treatment["environment"]
    assert control["model"]["model_name"] == treatment["model"]["model_name"]
    assert (
        control["agent"]["instance_template"] == treatment["agent"]["instance_template"]
    )


def test_skill_content_stripping(tmp_path):
    """Test that skill content whitespace is stripped."""
    skill_file = tmp_path / "skill.md"
    skill_file.write_text("\n\n  Test skill with whitespace  \n\n")

    config = build_treatment_config("test/model", skill_file)

    system_template = config["agent"]["system_template"]
    assert system_template.startswith("Test skill with whitespace")
    assert not system_template.startswith("\n")
    assert not system_template.startswith(" ")


def test_build_treatment_config_missing_file(tmp_path):
    """Test build_treatment_config raises FileNotFoundError for missing file."""
    nonexistent_file = tmp_path / "nonexistent.md"

    with pytest.raises(FileNotFoundError, match="Skill file not found"):
        build_treatment_config("test/model", nonexistent_file)

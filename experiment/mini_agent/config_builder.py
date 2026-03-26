import os
from pathlib import Path
from typing import Any


BASE_SYSTEM_TEMPLATE = (
    "You are a helpful assistant that can interact with a computer "
    "shell to solve programming tasks."
)

BASE_INSTANCE_TEMPLATE = """<pr_description>
Consider the following PR description:
{{task}}
</pr_description>

<instructions>
You're a software engineer interacting continuously with a computer by submitting commands.
Your task is to make changes to non-test files in the current directory to fix the issue described above.

For each response:
1. Include a THOUGHT section explaining your reasoning
2. Provide one or more bash tool calls to execute

Recommended Workflow:
1. Analyze the codebase by finding and reading relevant files
2. Create a script to reproduce the issue
3. Edit the source code to resolve the issue
4. Verify your fix works by running your script again
5. Test edge cases to ensure your fix is robust

When done, submit your changes:
1. Run `git diff -- path/to/file1 path/to/file2 > patch.txt`
2. Verify patch.txt contains only your intended changes
3. Run `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat patch.txt`
</instructions>"""


def build_config(
    model_name: str,
    skill_content: str | None = None,
    step_limit: int = 50,
    cost_limit: float = 3.0,
    temperature: float = 0.0,
    timeout: int = 60,
) -> dict[str, Any]:
    """Build mini-swe-agent config dict.

    Args:
        model_name: LiteLLM model name (e.g., "anthropic/claude-3-5-sonnet-20241022")
        skill_content: Optional skill text to prepend to system template
        step_limit: Max agent steps per task
        cost_limit: Max cost in USD per task
        temperature: LLM temperature
        timeout: Shell command timeout in seconds

    Returns:
        Config dict suitable for mini-swe-agent
    """
    system_template = BASE_SYSTEM_TEMPLATE
    if skill_content:
        system_template = skill_content.strip() + "\n\n---\n\n" + system_template

    litellm_model_name = model_name
    model_kwargs = {
        "drop_params": True,
        "temperature": temperature,
    }

    if model_name.startswith("nexos/"):
        litellm_model_name = f"openai/{model_name.split('/', 1)[1]}"
        model_kwargs["api_base"] = "https://api.nexos.ai/v1"
        nexos_key = os.environ.get("NEXOS_API_KEY")
        if nexos_key:
            model_kwargs["api_key"] = nexos_key

    return {
        "agent": {
            "system_template": system_template,
            "instance_template": BASE_INSTANCE_TEMPLATE,
            "step_limit": step_limit,
            "cost_limit": cost_limit,
        },
        "environment": {
            "cwd": "/testbed",
            "timeout": timeout,
            "interpreter": ["bash", "-c"],
            "env": {
                "PAGER": "cat",
                "MANPAGER": "cat",
                "LESS": "-R",
                "PIP_PROGRESS_BAR": "off",
                "TQDM_DISABLE": "1",
            },
            "environment_class": "docker",  # Required for mini-swe-agent isolation
        },
        "model": {
            "model_name": litellm_model_name,
            "model_kwargs": model_kwargs,
        },
    }


def build_control_config(
    model_name: str,
    **kwargs,
) -> dict[str, Any]:
    """Build config for control condition (no skill)."""
    return build_config(model_name, skill_content=None, **kwargs)


def build_treatment_config(
    model_name: str,
    skill_path: Path,
    **kwargs,
) -> dict[str, Any]:
    """Build config for treatment condition (with skill).

    Args:
        model_name: LiteLLM model name
        skill_path: Path to skill file to load
        **kwargs: Additional arguments passed to build_config

    Returns:
        Config dict with skill content prepended to system template

    Raises:
        FileNotFoundError: If skill_path does not exist
    """
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    skill_content = skill_path.read_text()
    return build_config(model_name, skill_content=skill_content, **kwargs)

# mini-swe-agent Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace single-turn API calls with multi-turn agentic execution using mini-swe-agent for realistic A/B testing of the Laws of Simplicity skill

**Architecture:** Use mini-swe-agent's Python API with its built-in SWE-bench config. Create two YAML configs (control/treatment), run each task via `DefaultAgent.run()`, and parse trajectory output for metrics (wall-clock time, tokens, turns, resolution).

**Tech Stack:** `mini-swe-agent` (v2.2.7), `litellm`, Docker, existing experiment framework

---

## File Structure

```
experiment/
├── mini_agent/
│   ├── __init__.py              # Exports MiniAgentRunner
│   ├── runner.py                # MiniAgentRunner: wraps mini-swe-agent Python API
│   ├── config_builder.py        # Build YAML configs for control/treatment
│   └── trajectory_parser.py     # Extract metrics from agent trajectory
├── config.py                    # Add runner_type="mini_agent"
└── runner.py                    # Add mini_agent runner selection
tests/
├── test_mini_agent_config.py    # Test config generation
└── test_trajectory_parser.py    # Test metric extraction from trajectories
```

## Chunk 1: Config Builder and Trajectory Parser

### Task 1: Add mini-swe-agent dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Verify mini-swe-agent is in dependencies**

It was already installed via `uv add mini-swe-agent`. Verify it's in `pyproject.toml`:

Run: `grep mini-swe-agent pyproject.toml`
Expected: `"mini-swe-agent>=2.2.0"`

If not present, add it to dependencies list.

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add mini-swe-agent for multi-turn experiment execution"
```

### Task 2: Create config builder

**Files:**
- Create: `experiment/mini_agent/__init__.py`
- Create: `experiment/mini_agent/config_builder.py`

- [ ] **Step 1: Create __init__.py**

```python
# experiment/mini_agent/__init__.py
```

- [ ] **Step 2: Create config_builder.py**

This module builds mini-swe-agent YAML config dicts for control and treatment conditions. The key difference: treatment prepends the Laws of Simplicity skill to the `system_template`.

```python
# experiment/mini_agent/config_builder.py
import copy
from pathlib import Path
from typing import Any


# Base SWE-bench system template from mini-swe-agent's default config
BASE_SYSTEM_TEMPLATE = (
    "You are a helpful assistant that can interact with a computer "
    "shell to solve programming tasks."
)

# Base SWE-bench instance template (the task prompt wrapper)
# Uses Jinja2 {{task}} variable that mini-swe-agent fills in
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
            "environment_class": "docker",
        },
        "model": {
            "model_name": model_name,
            "model_kwargs": {
                "drop_params": True,
                "temperature": temperature,
            },
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
    """Build config for treatment condition (with skill)."""
    skill_content = skill_path.read_text()
    return build_config(model_name, skill_content=skill_content, **kwargs)
```

- [ ] **Step 3: Commit**

```bash
git add experiment/mini_agent/
git commit -m "feat: add mini-swe-agent config builder for control/treatment conditions"
```

### Task 3: Create trajectory parser

**Files:**
- Create: `experiment/mini_agent/trajectory_parser.py`

- [ ] **Step 1: Create trajectory_parser.py**

This extracts metrics from mini-swe-agent's run output. The `DefaultAgent.run()` returns a dict with trajectory data.

```python
# experiment/mini_agent/trajectory_parser.py
from typing import Any


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
    import json
    from pathlib import Path
    
    path = Path(trajectory_path)
    if not path.exists():
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "num_turns": 0,
            "cost": 0.0,
            "exit_status": "not_found",
            "patch": "",
        }
    
    with open(path) as f:
        data = json.load(f)
    
    return parse_run_result(data)
```

- [ ] **Step 2: Commit**

```bash
git add experiment/mini_agent/trajectory_parser.py
git commit -m "feat: add trajectory parser for mini-swe-agent metrics extraction"
```

### Task 4: Write tests for config builder and trajectory parser

**Files:**
- Create: `tests/test_mini_agent_config.py`
- Create: `tests/test_trajectory_parser.py`

- [ ] **Step 1: Write config builder tests**

```python
# tests/test_mini_agent_config.py
from pathlib import Path

from experiment.mini_agent.config_builder import (
    build_config,
    build_control_config,
    build_treatment_config,
    BASE_SYSTEM_TEMPLATE,
)


def test_control_config_no_skill():
    config = build_control_config("anthropic/claude-3-5-sonnet-20241022")
    assert config["agent"]["system_template"] == BASE_SYSTEM_TEMPLATE
    assert config["model"]["model_name"] == "anthropic/claude-3-5-sonnet-20241022"


def test_treatment_config_has_skill(tmp_path):
    skill_file = tmp_path / "test-skill.md"
    skill_file.write_text("# Laws of Simplicity\n\nAlways keep it simple.")
    
    config = build_treatment_config("anthropic/claude-3-5-sonnet-20241022", skill_file)
    assert "Laws of Simplicity" in config["agent"]["system_template"]
    assert "Always keep it simple" in config["agent"]["system_template"]
    assert BASE_SYSTEM_TEMPLATE in config["agent"]["system_template"]


def test_skill_prepended_not_appended(tmp_path):
    skill_file = tmp_path / "skill.md"
    skill_file.write_text("SKILL_MARKER")
    
    config = build_treatment_config("test/model", skill_file)
    template = config["agent"]["system_template"]
    skill_pos = template.index("SKILL_MARKER")
    base_pos = template.index("helpful assistant")
    assert skill_pos < base_pos


def test_config_model_params():
    config = build_config("nexos/claude-4-5-sonnet", temperature=0.5, step_limit=30)
    assert config["model"]["model_kwargs"]["temperature"] == 0.5
    assert config["agent"]["step_limit"] == 30
```

- [ ] **Step 2: Write trajectory parser tests**

```python
# tests/test_trajectory_parser.py
import json

from experiment.mini_agent.trajectory_parser import (
    parse_run_result,
    parse_serialized_trajectory,
)


def test_parse_run_result():
    result = {
        "info": {
            "model_stats": {
                "tokens_sent": 45000,
                "tokens_received": 3200,
                "api_calls": 12,
                "instance_cost": 0.45,
            },
            "exit_status": "submitted",
            "submission": "diff --git a/foo.py b/foo.py\n",
        }
    }
    
    metrics = parse_run_result(result)
    assert metrics["input_tokens"] == 45000
    assert metrics["output_tokens"] == 3200
    assert metrics["num_turns"] == 12
    assert metrics["cost"] == 0.45
    assert metrics["exit_status"] == "submitted"
    assert "diff" in metrics["patch"]


def test_parse_empty_result():
    metrics = parse_run_result({})
    assert metrics["input_tokens"] == 0
    assert metrics["output_tokens"] == 0
    assert metrics["num_turns"] == 0


def test_parse_serialized_file(tmp_path):
    trajectory = {
        "info": {
            "model_stats": {
                "tokens_sent": 1000,
                "tokens_received": 500,
                "api_calls": 5,
                "instance_cost": 0.10,
            },
            "exit_status": "submitted",
            "submission": "patch content",
        }
    }
    path = tmp_path / "trajectory.json"
    path.write_text(json.dumps(trajectory))
    
    metrics = parse_serialized_trajectory(str(path))
    assert metrics["input_tokens"] == 1000
    assert metrics["num_turns"] == 5


def test_parse_missing_file():
    metrics = parse_serialized_trajectory("/nonexistent/path.json")
    assert metrics["exit_status"] == "not_found"
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest tests/test_mini_agent_config.py tests/test_trajectory_parser.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_mini_agent_config.py tests/test_trajectory_parser.py
git commit -m "test: add tests for mini-swe-agent config builder and trajectory parser"
```

## Chunk 2: Runner and Integration

### Task 5: Create MiniAgentRunner

**Files:**
- Create: `experiment/mini_agent/runner.py`

- [ ] **Step 1: Create runner.py**

```python
# experiment/mini_agent/runner.py
import logging
import time
from pathlib import Path
from typing import Any

from experiment.mini_agent.config_builder import build_control_config, build_treatment_config
from experiment.mini_agent.trajectory_parser import parse_run_result


class MiniAgentRunner:
    """Runs SWE-bench tasks using mini-swe-agent for multi-turn agentic execution."""
    
    def __init__(
        self,
        model_name: str,
        step_limit: int = 50,
        cost_limit: float = 3.0,
        temperature: float = 0.0,
        output_dir: Path | None = None,
    ):
        self.model_name = model_name
        self.step_limit = step_limit
        self.cost_limit = cost_limit
        self.temperature = temperature
        self.output_dir = output_dir
    
    def create_fresh_context(self, skills: list[Path] | None = None) -> dict[str, Any]:
        """Create context with optional skill loading.
        
        Args:
            skills: List of skill file paths (only first is used for system prompt)
            
        Returns:
            Context dict with config for mini-swe-agent
        """
        if skills and len(skills) > 0:
            config = build_treatment_config(
                self.model_name,
                skill_path=skills[0],
                step_limit=self.step_limit,
                cost_limit=self.cost_limit,
                temperature=self.temperature,
            )
        else:
            config = build_control_config(
                self.model_name,
                step_limit=self.step_limit,
                cost_limit=self.cost_limit,
                temperature=self.temperature,
            )
        
        return {"config": config, "skill_content": "" if not skills else "loaded"}
    
    def run_agent(
        self,
        ctx: dict[str, Any],
        task_prompt: str,
        timeout: int = 600,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Run mini-swe-agent on a task.
        
        Args:
            ctx: Context from create_fresh_context
            task_prompt: The task description (SWE-bench problem statement)
            timeout: Overall timeout in seconds
            max_tokens: Unused (mini-swe-agent manages this internally)
            
        Returns:
            Dict with input_tokens, output_tokens, output, iterations, etc.
        """
        from minisweagent.agents.default import DefaultAgent, AgentConfig
        from minisweagent.models.litellm_model import LitellmModel, LitellmModelConfig
        from minisweagent.environments.local import LocalEnvironment
        
        config = ctx["config"]
        
        model = LitellmModel(
            model_name=config["model"]["model_name"],
            model_kwargs=config["model"].get("model_kwargs", {}),
        )
        
        env = LocalEnvironment()
        
        agent = DefaultAgent(
            model=model,
            env=env,
            system_template=config["agent"]["system_template"],
            instance_template=config["agent"]["instance_template"],
            step_limit=config["agent"].get("step_limit", 50),
            cost_limit=config["agent"].get("cost_limit", 3.0),
        )
        
        start_time = time.time()
        
        try:
            result = agent.run(task=task_prompt)
            elapsed = time.time() - start_time
            
            metrics = parse_run_result(result)
            
            if self.output_dir:
                agent.save(str(self.output_dir))
            
            return {
                "input_tokens": metrics["input_tokens"],
                "output_tokens": metrics["output_tokens"],
                "output": metrics["patch"],
                "iterations": metrics["num_turns"],
                "return_code": 0 if metrics["exit_status"] == "submitted" else 1,
                "time_seconds": elapsed,
                "num_turns": metrics["num_turns"],
                "cost": metrics["cost"],
                "exit_status": metrics["exit_status"],
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            logging.error(f"mini-swe-agent error: {e}")
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "output": "",
                "iterations": 0,
                "return_code": 1,
                "time_seconds": elapsed,
                "num_turns": 0,
                "cost": 0.0,
                "exit_status": "error",
                "error": str(e),
            }
    
    def cleanup(self, ctx: dict[str, Any]) -> None:
        """Cleanup (no-op for mini-swe-agent)."""
        pass
```

- [ ] **Step 2: Update __init__.py**

```python
# experiment/mini_agent/__init__.py
from experiment.mini_agent.runner import MiniAgentRunner

__all__ = ["MiniAgentRunner"]
```

- [ ] **Step 3: Commit**

```bash
git add experiment/mini_agent/
git commit -m "feat: add MiniAgentRunner for multi-turn agentic execution"
```

### Task 6: Integrate with ExperimentConfig and ExperimentRunner

**Files:**
- Modify: `experiment/config.py`
- Modify: `experiment/runner.py`

- [ ] **Step 1: Add mini_agent to runner_type in config.py**

In `experiment/config.py`, change:

```python
runner_type: Literal["api", "cli"] = "api"
```

to:

```python
runner_type: Literal["api", "cli", "mini_agent"] = "api"
```

Also add mini-swe-agent specific fields:

```python
# mini-swe-agent configuration (only used when runner_type="mini_agent")
step_limit: int = 50
cost_limit: float = 3.0
```

- [ ] **Step 2: Add mini_agent runner selection in runner.py**

In the `__init__` method, add after the `elif self.config.runner_type == "cli"` block:

```python
elif self.config.runner_type == "mini_agent":
    from experiment.mini_agent.runner import MiniAgentRunner
    from experiment.providers import ModelConfig
    
    model_config = ModelConfig.from_string(self.config.model_string)
    # Convert to litellm model name format
    litellm_model = f"{model_config.provider}/{model_config.model}"
    
    self.runner = MiniAgentRunner(
        model_name=litellm_model,
        step_limit=self.config.step_limit,
        cost_limit=self.config.cost_limit,
        temperature=self.config.temperature,
        output_dir=self.config.raw_data_dir,
    )
```

Also add `"mini_agent"` to the `--runner-type` choices in the `main()` argparse section.

- [ ] **Step 3: Update the experiment start display**

Add `mini_agent` case to the run() method's display:

```python
if self.config.runner_type in ("api", "mini_agent"):
    print(f"  Model: {self.config.model_string}")
    print(f"  Temperature: {self.config.temperature}")
```

If `mini_agent`, also print:

```python
if self.config.runner_type == "mini_agent":
    print(f"  Step limit: {self.config.step_limit}")
    print(f"  Cost limit: ${self.config.cost_limit}")
```

- [ ] **Step 4: Run all tests**

Run: `uv run pytest -xvs`
Expected: All tests pass (existing + new)

- [ ] **Step 5: Commit**

```bash
git add experiment/config.py experiment/runner.py
git commit -m "feat: integrate mini-swe-agent as runner_type in experiment framework"
```

### Task 7: Add analysis output for turns metric

**Files:**
- Modify: `experiment/runner.py` (main() analysis output)

- [ ] **Step 1: Add turns metric to analysis summary**

In the `main()` function, after the time-to-completion section, add:

```python
# If mini_agent runner, show turns metric
if args.runner_type == "mini_agent":
    import pandas as pd
    results_csv = config.results_dir / "aggregate_results.csv"
    if results_csv.exists():
        df = pd.read_csv(results_csv)
        if "iterations" in df.columns:
            ctrl = df[df["condition"] == "control"]["iterations"]
            treat = df[df["condition"] == "treatment"]["iterations"]
            print(f"\n🔄 Turns per Task:")
            print(f"  Control:   {ctrl.mean():.1f} turns (mean)")
            print(f"  Treatment: {treat.mean():.1f} turns (mean)")
            diff = treat.mean() - ctrl.mean()
            pct = (diff / ctrl.mean()) * 100 if ctrl.mean() > 0 else 0
            print(f"  Difference: {diff:+.1f} turns ({pct:+.1f}%)")
```

- [ ] **Step 2: Commit**

```bash
git add experiment/runner.py
git commit -m "feat: add turns-per-task metric to analysis summary for mini-agent"
```

### Task 8: Verify CLI works

- [ ] **Step 1: Test help output**

Run: `uv run python -m experiment.runner --help`
Expected: `--runner-type {api,cli,mini_agent}` shown in help

- [ ] **Step 2: Test dry run (will fail without Docker, but should parse args)**

Run: `uv run python -m experiment.runner --runner-type mini_agent --model "anthropic/claude-3-5-sonnet-20241022" --benchmarks swe_bench_lite --num-tasks 1 2>&1 | head -10`
Expected: Shows "Starting experiment:" with mini_agent config, then may fail at Docker step

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete mini-swe-agent integration for multi-turn experiments"
```

---

## Usage

### Pilot (n=5)

```bash
uv run python -m experiment.runner \
  --runner-type mini_agent \
  --model "nexos/Claude Sonnet 4.5 (Trusted)" \
  --benchmarks swe_bench_lite \
  --num-tasks 5 \
  --timeout 300
```

### Full Experiment (n=100)

```bash
uv run python -m experiment.runner \
  --runner-type mini_agent \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --benchmarks swe_bench_lite \
  --num-tasks 100 \
  --timeout 600
```

## Dependencies

- Docker daemon running (mini-swe-agent uses Docker for SWE-bench tasks)
- API key set for chosen provider (ANTHROPIC_API_KEY, NEXOS_API_KEY, etc.)
- ~50GB disk space for Docker images

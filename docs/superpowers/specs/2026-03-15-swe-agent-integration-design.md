# SWE-agent Integration Design Spec

**Date:** 2026-03-15
**Author:** AI-Provenance Team
**Status:** Draft

## Problem

Our current experiment sends a single API call per task. The Laws of Simplicity skill adds ~1,251 tokens to the system prompt, which can only increase cost and time. There is no opportunity for the skill to reduce wasted exploration or prevent dead-end iterations.

The AGENTS.md paper showed 20-29% time reduction because their skill file prevented agents from wasting turns exploring project structure. To measure whether the Laws of Simplicity skill has a similar effect, we need **multi-turn agentic execution** where the agent explores code, makes edits, and runs tests across many turns.

## Solution

Integrate [SWE-agent](https://github.com/SWE-agent/SWE-agent) as the execution engine. SWE-agent is the standard agent harness for SWE-bench tasks. It:

- Clones repos at the correct commit in Docker containers
- Gives the LLM a shell-based interface (search, edit, test)
- Tracks tokens, turns, and wall-clock time per run
- Verifies solutions by running the task's test suite

## Architecture

```
experiment/
├── config.py                    # Add SWE-agent config fields
├── runner.py                    # Orchestrate SWE-agent runs
├── providers/                   # Existing - provides model config
├── harness/
│   └── swe_bench.py             # Update to use SWE-agent for execution
└── swe_agent/
    ├── __init__.py
    ├── runner.py                # SWEAgentRunner: wraps SWE-agent CLI
    ├── config_generator.py      # Generate SWE-agent YAML configs
    └── metrics_parser.py        # Parse SWE-agent output logs for metrics
```

### Flow

```
ExperimentRunner.run()
  │
  ├── For each task_id in SWE-bench Lite (n=100):
  │   │
  │   ├── Determine condition order: hash(task_id) % 2
  │   │
  │   ├── Run Condition A:
  │   │   ├── SWEAgentRunner.run(task_id, system_prompt=base_prompt)
  │   │   │   ├── Generate SWE-agent config YAML (no skill)
  │   │   │   ├── Invoke: sweagent run --config control.yaml --task task_id
  │   │   │   │   └── Docker container: clone repo → agent loop → patch
  │   │   │   ├── Parse trajectory log for metrics
  │   │   │   └── Return: {wall_time, input_tokens, output_tokens, turns, resolved}
  │   │   └── Store results
  │   │
  │   └── Run Condition B:
  │       ├── SWEAgentRunner.run(task_id, system_prompt=base_prompt + skill)
  │       │   ├── Generate SWE-agent config YAML (with skill prepended)
  │       │   ├── Invoke: sweagent run --config treatment.yaml --task task_id
  │       │   │   └── Docker container: clone repo → agent loop → patch
  │       │   ├── Parse trajectory log for metrics
  │       │   └── Return: {wall_time, input_tokens, output_tokens, turns, resolved}
  │       └── Store results
  │
  └── Aggregate + Analyze (existing pipeline)
```

## SWE-agent Configuration

SWE-agent uses YAML config files. We need two:

### Control Config

```yaml
agent:
  model:
    name: "claude-sonnet-4-5-20250514"
    api_key_env: "ANTHROPIC_API_KEY"
    temperature: 0.0
    per_instance_cost_limit: 3.00
  system_template: |
    SETTING: You are an autonomous programmer...
    [standard SWE-agent system prompt]
```

### Treatment Config

```yaml
agent:
  model:
    name: "claude-sonnet-4-5-20250514"
    api_key_env: "ANTHROPIC_API_KEY"
    temperature: 0.0
    per_instance_cost_limit: 3.00
  system_template: |
    [Laws of Simplicity skill content prepended]
    
    ---
    
    SETTING: You are an autonomous programmer...
    [standard SWE-agent system prompt]
```

### Model Configuration

SWE-agent supports multiple model providers. Our existing ModelConfig maps to SWE-agent's model config:

| Our Config | SWE-agent Config |
|---|---|
| `anthropic/claude-3-5-sonnet` | `model.name: claude-3-5-sonnet-20241022` |
| `openai/gpt-4-turbo` | `model.name: gpt-4-turbo` |
| `nexos/Claude Sonnet 4.5` | `model.name: Claude Sonnet 4.5`, `model.api_base: https://api.nexos.ai/v1` |

## Metrics Collection

### SWE-agent Output

SWE-agent produces trajectory logs in JSON format containing:

```json
{
  "info": {
    "model_stats": {
      "instance_cost": 0.45,
      "tokens_sent": 45000,
      "tokens_received": 3200,
      "api_calls": 12
    },
    "exit_status": "submitted",
    "submission": "diff --git a/... "
  },
  "trajectory": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "thought": "..."},
    {"role": "tool", "content": "..."}
  ]
}
```

### What We Extract

| Metric | Source | Description |
|---|---|---|
| `wall_clock_time` | `time.time()` around run | Total elapsed seconds |
| `input_tokens` | `info.model_stats.tokens_sent` | Total input tokens across all turns |
| `output_tokens` | `info.model_stats.tokens_received` | Total output tokens across all turns |
| `num_turns` | `info.model_stats.api_calls` | Number of LLM calls (turns) |
| `resolved` | SWE-bench evaluation | Whether the patch passes tests |
| `cost` | `info.model_stats.instance_cost` | Estimated dollar cost |
| `exit_status` | `info.exit_status` | How the agent stopped (submitted/timeout/error) |

### Mapping to Research Questions

| RQ | Primary Metric | Test |
|---|---|---|
| RQ1: Time reduction | `wall_clock_time` | Wilcoxon signed-rank |
| RQ2: Quality impact | `resolved` | McNemar's test |
| RQ3: Token cost | `input_tokens + output_tokens` | Paired t-test |
| RQ4: Task heterogeneity | `wall_clock_time` by difficulty | Two-way ANOVA |
| NEW: Iteration reduction | `num_turns` | Paired t-test |

## SWEAgentRunner Interface

```python
class SWEAgentRunner:
    """Wraps SWE-agent CLI for controlled experiment execution."""
    
    def __init__(self, model_config: ModelConfig, output_dir: Path):
        """Initialize with model configuration."""
    
    def run(
        self,
        task_id: str,
        skill_content: str | None = None,
        timeout: int = 600,
    ) -> dict:
        """Run SWE-agent on a single task.
        
        Args:
            task_id: SWE-bench instance ID (e.g., "django__django-13551")
            skill_content: Optional skill text to prepend to system prompt
            timeout: Max seconds per task
            
        Returns:
            {
                "wall_clock_time": float,
                "input_tokens": int,
                "output_tokens": int,
                "num_turns": int,
                "resolved": bool,
                "cost": float,
                "exit_status": str,
                "patch": str,
            }
        """
    
    def _generate_config(self, skill_content: str | None) -> Path:
        """Generate SWE-agent YAML config file."""
    
    def _parse_trajectory(self, trajectory_path: Path) -> dict:
        """Parse SWE-agent trajectory log for metrics."""
```

## Integration with ExperimentRunner

The existing `ExperimentRunner._run_task()` needs to be updated to use `SWEAgentRunner` when `runner_type="swe_agent"`:

```python
# experiment/config.py
runner_type: Literal["api", "cli", "swe_agent"] = "swe_agent"
```

```python
# experiment/runner.py
if self.config.runner_type == "swe_agent":
    from experiment.swe_agent.runner import SWEAgentRunner
    self.runner = SWEAgentRunner(model_config, self.config.raw_data_dir)
```

## Prerequisites

### Installation

```bash
pip install sweagent
# or
uv add sweagent
```

### Docker

SWE-agent requires Docker for containerized execution:

```bash
docker pull sweagent/swe-agent:latest
```

### API Keys

Set the API key for your chosen provider:

```bash
export ANTHROPIC_API_KEY="..."
# or
export NEXOS_API_KEY="..."
```

## Execution Plan

### Pilot (n=5, ~30 min)

```bash
uv run python -m experiment.runner \
  --runner-type swe_agent \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --benchmarks swe_bench_lite \
  --num-tasks 5
```

### Full Experiment (n=100, ~7-17 hours)

```bash
uv run python -m experiment.runner \
  --runner-type swe_agent \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --benchmarks swe_bench_lite \
  --num-tasks 100 \
  --timeout 600
```

### Expected Output

```
Starting experiment:
  Runner: swe_agent
  Model: anthropic/claude-3-5-sonnet-20241022
  Benchmarks: swe_bench_lite
  Tasks per benchmark: 5
  Conditions: control, treatment

[1/5] Task: django__django-13551
  Running control...
    Turns: 8, Time: 95.2s, Tokens: 45,230, Resolved: True
  Running treatment...
    Turns: 5, Time: 72.1s, Tokens: 38,450, Resolved: True

=== Analysis Summary ===
Time-to-Completion (PRIMARY METRIC):
  Control:   98.6s (median)
  Treatment: 74.2s (median)
  Difference: -24.4s (-24.7%)

Turns per Task:
  Control:   8.2 (mean)
  Treatment: 5.8 (mean)
  Difference: -2.4 turns (-29.3%)

Token Usage:
  Control:   42,100 tokens (mean)
  Treatment: 36,800 tokens (mean)
  Difference: -5,300 tokens (-12.6%)

Resolution Rate:
  Control:   52.0%
  Treatment: 48.0%
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| SWE-agent version incompatibility | Blocks experiment | Pin version, test with pilot first |
| Docker resource exhaustion | Crashes mid-experiment | Set per-task resource limits, checkpoint results |
| Cost overrun | Budget exceeded | Set per_instance_cost_limit in config |
| Long execution time | Delays results | Start with pilot (n=5), parallelize if possible |
| SWE-agent doesn't support Nexos.ai | Can't use preferred model | Use Anthropic directly, or configure custom base_url |

## Out of Scope

- HumanEval benchmark (single-function tasks don't benefit from multi-turn)
- Custom tool implementations (use SWE-agent's built-in tools)
- Parallel execution (run sequentially for reproducibility)
- Code quality metrics beyond test pass rate (future work)

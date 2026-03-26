# Laws of Simplicity Experiment Status

**Last Updated:** 2026-03-17
**Status:** READY FOR EXECUTION

---

## Recent Changes

### 2026-03-17: Framework Simplification

Simplified the experiment framework to focus on the core research question:

- **Removed:** Provider abstraction layer, CLI runner, API runner, HumanEval benchmark
- **Removed:** McNemar's test (RQ2), two-way ANOVA (RQ3), Mann-Whitney U
- **Removed:** Solution verification stubs
- **Kept:** mini-swe-agent runner (multi-turn), SWE-bench Lite, paired t-test + bootstrap CI
- **Impact:** ~1,100 lines of dead code removed, framework focused on RQ1 only

### 2026-03-15: Direct API Integration (Historical)

Switched from OpenCode CLI to direct LLM API calls. This was later superseded by the mini-swe-agent integration.

---

## Summary

Automated A/B experiment runner measuring token reduction from the Laws of Simplicity skill.

## Research Design

### Research Question

**RQ1:** Does the Laws of Simplicity skill reduce token consumption in multi-turn agentic coding tasks?

### A/B Controlled Study

- **Control:** Agent with default system prompt only
- **Treatment:** Agent with Laws of Simplicity skill prepended to system prompt
- **Runner:** mini-swe-agent (multi-turn agentic execution)
- **Benchmark:** SWE-bench Lite (real-world GitHub issues)
- **Counterbalancing:** `hash(task_id) % 2` determines condition order
- **Sample Size:** 100 tasks (powered for Cohen's d=0.3)

### Metrics

| Metric | Type | Measurement |
|--------|------|-------------|
| Total tokens | Primary | mini-swe-agent trajectory |
| Turns per task | Secondary | Agent step count |
| Time-to-completion | Secondary | Wall-clock time |
| Cost | Secondary | LLM API cost |

### Statistical Analysis

- Paired t-test with Cohen's d effect size
- Bootstrap 95% CI (10,000 resamples, percentile method)

## Running the Experiment

```bash
uv run python -m experiment --model "anthropic/claude-3-5-sonnet-20241022" --num-tasks 5
```

## Output Files

```
data/
├── raw/
│   ├── task_id_control.json
│   ├── task_id_treatment.json
│   └── trajectories/
└── results/
    ├── aggregate_results.csv
    ├── task_metadata.json
    └── analysis.json
```

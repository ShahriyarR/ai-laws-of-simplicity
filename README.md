# AI Laws of Simplicity

A standalone skill that guides AI agents to apply [John Maeda's 10 Laws of Simplicity](https://lawsofsimplicity.com/) throughout the software development lifecycle.

## Overview

This repository contains:

1. **A skill for AI coding agents** that helps them apply the principles from John Maeda's "The Laws of Simplicity" to software development
2. **An experiment framework** to measure whether the skill reduces token consumption in multi-turn agentic coding tasks

## The 10 Laws of Simplicity

1. **REDUCE**: The simplest way to achieve simplicity is through thoughtful reduction.
2. **ORGANIZE**: Organization makes a system of many appear fewer.
3. **TIME**: Savings in time feel like simplicity.
4. **LEARN**: Knowledge makes everything simpler.
5. **DIFFERENCES**: Simplicity and complexity need each other.
6. **CONTEXT**: What lies in the periphery of simplicity is definitely not peripheral.
7. **EMOTION**: More emotions are better than less.
8. **TRUST**: In simplicity we trust.
9. **FAILURE**: Some things can never be made simple.
10. **THE ONE**: Simplicity is about subtracting the obvious, and adding the meaningful.

## Installation

To install this skill in your AI coding agent:

### For OpenCode Users

Tell OpenCode to fetch and follow the installation instructions:
```
Fetch and follow instructions from https://raw.githubusercontent.com/AI-Provenance/ai-laws-of-simplicity/main/INSTALL.md
```

### For Claude Code Users

Copy the skill to Claude Code's global skills directory:

```bash
mkdir -p ~/.claude/skills/laws-of-simplicity
curl -o ~/.claude/skills/laws-of-simplicity/SKILL.md \
  https://raw.githubusercontent.com/AI-Provenance/ai-laws-of-simplicity/main/skills/laws-of-simplicity/SKILL.md
```

The skill will be available in all Claude Code sessions. Invoke it with:

```
/laws-of-simplicity
```

### For Other Platforms

See the [INSTALL.md](INSTALL.md) file for detailed instructions.

## Running the Experiment

The experiment uses [mini-swe-agent](https://github.com/princeton-nlp/SWE-agent) for multi-turn agentic execution against SWE-bench Lite tasks.

### Quick Start

```bash
uv run python -m experiment --model "anthropic/claude-3-5-sonnet-20241022" --num-tasks 5
```

### CLI Options

```
--model       LiteLLM model string (default: anthropic/claude-3-5-sonnet-20241022)
--num-tasks   Number of tasks per benchmark (default: 100)
--temperature LLM temperature (default: 0.0)
--timeout     Timeout in seconds per task (default: 600)
```

### Docker

```bash
docker build -t simplicity-experiment .
docker run -v $(pwd)/data:/app/data simplicity-experiment --num-tasks 5
```

## Files

- `skills/laws-of-simplicity/SKILL.md` — The skill file
- `experiment/` — Experiment framework
- `INSTALL.md` — Installation guide

## License

Based on "The Laws of Simplicity" by John Maeda.

## Contributing

Contributions welcome! Please submit a Pull Request.

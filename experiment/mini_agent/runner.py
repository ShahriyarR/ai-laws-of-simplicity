import logging
import time
from pathlib import Path
from typing import Any

from experiment.mini_agent.config_builder import (
    build_control_config,
    build_treatment_config,
)
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
        import os
        from minisweagent.agents.default import DefaultAgent
        from minisweagent.models.litellm_model import LitellmModel
        from minisweagent.environments.local import LocalEnvironment

        os.environ.setdefault("MSWEA_COST_TRACKING", "ignore_errors")

        config = ctx["config"]

        model = LitellmModel(
            model_name=config["model"]["model_name"],
            model_kwargs=config["model"].get("model_kwargs", {}),
        )

        import tempfile

        workdir = tempfile.mkdtemp(prefix="mini_agent_")
        env = LocalEnvironment(cwd=workdir)

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
            agent.run(task=task_prompt)
            elapsed = time.time() - start_time

            metrics = parse_run_result(agent.serialize())

            if self.output_dir:
                traj_dir = self.output_dir / "trajectories"
                traj_dir.mkdir(parents=True, exist_ok=True)
                task_id = task_prompt[:80].replace("/", "_").replace(" ", "_")
                condition = "treatment" if ctx.get("skill_content") else "control"
                trajectory_file = traj_dir / f"{task_id}_{condition}.json"
                agent.save(trajectory_file)

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

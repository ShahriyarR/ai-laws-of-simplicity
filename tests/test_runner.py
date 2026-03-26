import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner


@pytest.fixture
def config(tmp_path):
    return ExperimentConfig(
        benchmarks=["swe_bench_lite"],
        num_tasks_per_benchmark=2,
        model_string="anthropic/claude-3-5-sonnet-20241022",
        raw_data_dir=tmp_path / "raw",
        results_dir=tmp_path / "results",
    )


class TestExperimentRunner:
    @patch("experiment.runner.SWEBenchHarness")
    @patch("experiment.runner.MiniAgentRunner")
    def test_init_creates_dirs(self, mock_mini, mock_harness, config):
        runner = ExperimentRunner(config)

        assert config.raw_data_dir.exists()
        assert config.results_dir.exists()

    @patch("experiment.runner.SWEBenchHarness")
    @patch("experiment.runner.MiniAgentRunner")
    def test_runs_both_conditions_per_task(
        self, mock_mini_cls, mock_harness_cls, config
    ):
        from experiment.harness.base import TaskSpec

        mock_harness = mock_harness_cls.return_value
        mock_harness.load_tasks.return_value = [
            TaskSpec(
                task_id="test-task-1",
                benchmark="swe_bench_lite",
                prompt="Fix the bug",
                test_file=None,
                expected_solution=None,
                difficulty="simple",
            ),
        ]

        mock_runner = mock_mini_cls.return_value
        mock_runner.create_fresh_context.return_value = {
            "config": {},
            "skill_content": "",
        }
        mock_runner.run_agent.return_value = {
            "input_tokens": 100,
            "output_tokens": 50,
            "output": "patch",
            "iterations": 3,
        }
        mock_runner.cleanup.return_value = None

        runner = ExperimentRunner(config)
        runner.run()

        assert mock_runner.run_agent.call_count == 2

    @patch("experiment.runner.SWEBenchHarness")
    @patch("experiment.runner.MiniAgentRunner")
    def test_counterbalancing(self, mock_mini_cls, mock_harness_cls, config):
        from experiment.harness.base import TaskSpec

        mock_harness = mock_harness_cls.return_value
        mock_harness.load_tasks.return_value = [
            TaskSpec(
                task_id="task-a",
                benchmark="swe_bench_lite",
                prompt="Fix bug A",
                test_file=None,
                expected_solution=None,
                difficulty="simple",
            ),
            TaskSpec(
                task_id="task-b",
                benchmark="swe_bench_lite",
                prompt="Fix bug B",
                test_file=None,
                expected_solution=None,
                difficulty="medium",
            ),
        ]

        mock_runner = mock_mini_cls.return_value
        mock_runner.create_fresh_context.return_value = {
            "config": {},
            "skill_content": "",
        }
        mock_runner.run_agent.return_value = {
            "input_tokens": 100,
            "output_tokens": 50,
            "output": "patch",
            "iterations": 3,
        }
        mock_runner.cleanup.return_value = None

        runner = ExperimentRunner(config)
        runner.run()

        assert mock_runner.run_agent.call_count == 4

"""Integration tests for RepoLens closed-loop multi-agent orchestrator."""

import unittest
from pathlib import Path
from src.config import SystemConfig, AblationConfig
from src.pipeline.orchestrator import RepoLensOrchestrator


class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"
        self.repo_path = self.benchmarks_dir / "py_small_kv"

    def test_full_pipeline_execution(self):
        config = SystemConfig()
        orchestrator = RepoLensOrchestrator(config)
        output = orchestrator.run(self.repo_path, "py_small_kv")

        self.assertEqual(output.repo_name, "py_small_kv")
        self.assertTrue(output.verification_report.is_valid)
        self.assertEqual(output.verification_report.total_hallucinations, 0)
        self.assertIn("# py_small_kv", output.readme_markdown)
        self.assertIn("flowchart TD", output.mermaid_diagram)
        self.assertTrue(len(output.trajectory.steps) >= 4)

    def test_ablation_mode_execution(self):
        ablation = AblationConfig(
            enable_ast_verification=False,
            enable_scanner_matrix=False,
            enable_programmatic_mermaid=False
        )
        config = SystemConfig(ablation=ablation)
        orchestrator = RepoLensOrchestrator(config)
        output = orchestrator.run(self.repo_path, "py_small_kv")

        self.assertEqual(output.repo_name, "py_small_kv")
        self.assertEqual(output.iterations_used, 1)
        self.assertFalse(output.ablation_flags["enable_ast_verification"])


if __name__ == "__main__":
    unittest.main()

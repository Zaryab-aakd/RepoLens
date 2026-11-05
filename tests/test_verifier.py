"""Deterministic unit tests for VerifierAgent hallucination detection."""

import unittest
from pathlib import Path
from src.config import SystemConfig
from src.logger import TrajectoryLogger
from src.ingestion.extractor import RepositoryExtractor
from src.agents.verifier_agent import VerifierAgent


class TestVerifierAgent(unittest.TestCase):

    def setUp(self):
        self.config = SystemConfig()
        self.logger = TrajectoryLogger("test_verifier")
        self.verifier = VerifierAgent(self.config, self.logger)
        self.extractor = RepositoryExtractor()
        benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"
        self.repo_ast = self.extractor.extract(benchmarks_dir / "py_small_math", "py_small_math")

    def test_valid_synthesis_verification(self):
        valid_md = """
# Math Repo
`dot_product(v1, v2)` calculates vector dot product.
`Vector2D.magnitude()` returns vector magnitude.
"""
        valid_mermaid = """
flowchart TD
    vector_py["vector.py"]
    matrix_py["matrix.py"]
    matrix_py --> vector_py
"""
        report = self.verifier.verify(self.repo_ast, valid_md, valid_mermaid)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.total_hallucinations, 0)
        self.assertEqual(report.hallucination_rate, 0.0)

    def test_detect_ghost_function_hallucination(self):
        invalid_md = """
# Math Repo
`ghost_matrix_solver(param1, param2)` solves nonexistent matrix equations.
"""
        valid_mermaid = "flowchart TD\n    vector_py[\"vector.py\"]"
        report = self.verifier.verify(self.repo_ast, invalid_md, valid_mermaid)
        self.assertFalse(report.is_valid)
        self.assertGreater(report.total_hallucinations, 0)
        ghost_issues = [i for i in report.issues if i.issue_type == "ghost_function"]
        self.assertEqual(len(ghost_issues), 1)
        self.assertIn("ghost_matrix_solver", ghost_issues[0].claim)

    def test_detect_parameter_mismatch(self):
        invalid_md = """
`dot_product(vector_a, vector_b, extra_nonexistent_param)`
"""
        valid_mermaid = "flowchart TD\n    vector_py[\"vector.py\"]"
        report = self.verifier.verify(self.repo_ast, invalid_md, valid_mermaid)
        self.assertFalse(report.is_valid)
        param_issues = [i for i in report.issues if i.issue_type == "signature_mismatch"]
        self.assertEqual(len(param_issues), 1)


if __name__ == "__main__":
    unittest.main()

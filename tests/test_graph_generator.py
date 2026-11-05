"""Deterministic unit tests for Dependency Graph and Mermaid Generator."""

import unittest
from pathlib import Path
from src.ingestion.extractor import RepositoryExtractor
from src.graph.dependency_graph import DependencyGraphBuilder
from src.graph.mermaid_generator import MermaidDiagramGenerator
from src.evaluation.metrics import compute_graph_edit_distance


class TestGraphAndMermaid(unittest.TestCase):

    def setUp(self):
        self.extractor = RepositoryExtractor()
        self.benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"
        self.repo_ast = self.extractor.extract(self.benchmarks_dir / "py_small_math", "py_small_math")
        self.builder = DependencyGraphBuilder(self.repo_ast)
        self.generator = MermaidDiagramGenerator(self.repo_ast, self.builder)

    def test_dependency_edges_exist(self):
        edges = self.builder.get_edge_list()
        self.assertTrue(len(edges) >= 2, "Matrix and main should import vector")
        # Check that matrix.py -> vector.py edge is recorded
        has_matrix_vector = any(
            "matrix.py" in src and "vector.py" in dst for src, dst in edges
        )
        self.assertTrue(has_matrix_vector)

    def test_mermaid_generation_and_parsing(self):
        mermaid_code = self.generator.generate_diagram()
        self.assertIn("flowchart TD", mermaid_code)
        parsed_nodes = MermaidDiagramGenerator.parse_mermaid_nodes(mermaid_code)
        parsed_edges = MermaidDiagramGenerator.parse_mermaid_edges(mermaid_code)
        self.assertTrue(len(parsed_nodes) >= 3)
        self.assertTrue(len(parsed_edges) >= 2)

    def test_ged_computation_zero_for_identical(self):
        nodes = {"a", "b", "c"}
        edges = [("a", "b"), ("b", "c")]
        ged_res = compute_graph_edit_distance(nodes, nodes, edges, edges)
        self.assertEqual(ged_res["raw_ged"], 0.0)
        self.assertEqual(ged_res["node_precision"], 1.0)
        self.assertEqual(ged_res["edge_precision"], 1.0)


if __name__ == "__main__":
    unittest.main()

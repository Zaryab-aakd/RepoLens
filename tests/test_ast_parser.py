"""Deterministic unit tests for Python and JS/TS AST parsers."""

import unittest
from pathlib import Path
from src.ingestion.python_parser import PythonASTParser
from src.ingestion.js_ts_parser import JavaScriptTypeScriptParser


class TestASTParsers(unittest.TestCase):

    def setUp(self):
        self.py_parser = PythonASTParser()
        self.js_parser = JavaScriptTypeScriptParser()
        self.benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"

    def test_python_symbol_extraction(self):
        math_file = self.benchmarks_dir / "py_small_math" / "vector.py"
        self.assertTrue(math_file.exists(), "vector.py should exist in benchmarks")

        symbols = self.py_parser.parse_file(math_file, relative_to=self.benchmarks_dir / "py_small_math")
        self.assertEqual(symbols.language, "python")
        self.assertIn("Vector2D", symbols.classes)
        self.assertIn("magnitude", symbols.classes["Vector2D"].methods)
        self.assertIn("normalize", symbols.classes["Vector2D"].methods)
        self.assertIn("dot_product", symbols.functions)
        self.assertEqual(symbols.functions["dot_product"].arguments, ["v1", "v2"])

    def test_python_route_detection(self):
        gateway_file = self.benchmarks_dir / "py_med_apigateway" / "router.py"
        symbols = self.py_parser.parse_file(gateway_file, relative_to=self.benchmarks_dir / "py_med_apigateway")
        self.assertIn("APIGateway", symbols.classes)
        self.assertIn("APIGateway.route_get", symbols.functions)
        self.assertEqual(symbols.functions["APIGateway.route_get"].arguments, ["path", "token", "ip"])

    def test_javascript_symbol_extraction(self):
        calc_file = self.benchmarks_dir / "js_small_calculator" / "evaluator.js"
        symbols = self.js_parser.parse_file(calc_file, relative_to=self.benchmarks_dir / "js_small_calculator")
        self.assertIn("evaluateExpression", symbols.functions)
        self.assertEqual(symbols.functions["evaluateExpression"].arguments, ["expr"])
        self.assertTrue(len(symbols.imports) > 0)


if __name__ == "__main__":
    unittest.main()

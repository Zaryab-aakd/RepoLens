"""Repository scanner and AST symbol table builder."""

from pathlib import Path
from typing import Set
from src.ingestion.python_parser import PythonASTParser
from src.ingestion.js_ts_parser import JavaScriptTypeScriptParser
from src.models import RepositoryAST


class RepositoryExtractor:
    """Recursively scans a repository and builds an AST symbol table."""

    IGNORED_DIRS: Set[str] = {
        ".git", ".github", ".venv", "venv", "env", "__pycache__",
        "node_modules", "dist", "build", ".pytest_cache", ".ruff_cache",
        ".mypy_cache", "coverage", ".next", ".nuxt"
    }

    def __init__(self):
        self.py_parser = PythonASTParser()
        self.js_ts_parser = JavaScriptTypeScriptParser()

    def extract(self, repo_path: Path, repo_name: str = "") -> RepositoryAST:
        repo_path = repo_path.resolve()
        name = repo_name or repo_path.name
        repo_ast = RepositoryAST(repo_name=name, repo_path=str(repo_path))

        total_loc = 0
        for p in repo_path.rglob("*"):
            if not p.is_file():
                continue
            # Check ignored directories
            if any(part in self.IGNORED_DIRS for part in p.parts):
                continue

            if p.suffix == ".py":
                file_sym = self.py_parser.parse_file(p, relative_to=repo_path)
                repo_ast.files[file_sym.file_path] = file_sym
                total_loc += file_sym.loc
            elif p.suffix in {".js", ".jsx", ".ts", ".tsx"}:
                file_sym = self.js_ts_parser.parse_file(p, relative_to=repo_path)
                repo_ast.files[file_sym.file_path] = file_sym
                total_loc += file_sym.loc

        repo_ast.total_loc = total_loc
        return repo_ast

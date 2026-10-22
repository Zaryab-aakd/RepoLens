"""Python AST symbol extractor using standard library ast module."""

import ast
from pathlib import Path
from typing import List, Optional
from src.ingestion.base import BaseASTParser
from src.models import ClassSymbol, FileSymbols, FunctionSymbol, ImportSymbol


class PythonCallVisitor(ast.NodeVisitor):
    """Collects all function calls within an AST block."""

    def __init__(self):
        self.calls: List[str] = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)


class PythonASTParser(BaseASTParser):
    """Extracts classes, functions, arguments, routes, imports, and calls from Python files."""

    def parse_file(self, file_path: Path, relative_to: Path) -> FileSymbols:
        rel_str = str(file_path.relative_to(relative_to)).replace("\\", "/")
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception:
                return FileSymbols(file_path=rel_str, language="python")

        loc = len([line for line in content.splitlines() if line.strip() and not line.strip().startswith("#")])
        symbols = FileSymbols(file_path=rel_str, language="python", loc=loc)

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return symbols

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._parse_import(node, symbols, rel_str)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._parse_function(node, rel_str, is_method=False)
                symbols.functions[fn.name] = fn
            elif isinstance(node, ast.ClassDef):
                cls = self._parse_class(node, rel_str)
                symbols.classes[cls.name] = cls
                for method_name, method_fn in self._extract_class_methods(node, rel_str, cls.name).items():
                    symbols.functions[method_fn.qualified_name] = method_fn

        return symbols

    def _parse_import(self, node: ast.AST, symbols: FileSymbols, file_path: str):
        if isinstance(node, ast.Import):
            for alias in node.names:
                symbols.imports.append(
                    ImportSymbol(module=alias.name, imported_names=[alias.asname or alias.name], file_path=file_path)
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = [alias.name for alias in node.names]
            symbols.imports.append(
                ImportSymbol(module=mod, imported_names=names, is_relative=(node.level > 0), file_path=file_path)
            )

    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        is_method: bool = False,
        class_name: Optional[str] = None
    ) -> FunctionSymbol:
        args = [a.arg for a in node.args.args if a.arg != "self" and a.arg != "cls"]
        ret_type = None
        if node.returns:
            ret_type = ast.unparse(node.returns) if hasattr(ast, "unparse") else None

        doc = ast.get_docstring(node)
        
        # Static calls inside the function
        call_visitor = PythonCallVisitor()
        call_visitor.visit(node)

        # Detect REST API routes in decorators (FastAPI/Flask)
        is_route = False
        route_path = None
        route_method = None
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute):
                    # e.g., @app.get("/items"), @router.post("/auth")
                    method_candidate = func.attr.lower()
                    if method_candidate in {"get", "post", "put", "delete", "patch", "route"}:
                        is_route = True
                        route_method = method_candidate.upper()
                        if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                            route_path = dec.args[0].value
                elif isinstance(func, ast.Name) and func.id in {"route", "get", "post"}:
                    is_route = True
                    route_method = func.id.upper()
                    if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                        route_path = dec.args[0].value

        return FunctionSymbol(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            arguments=args,
            return_type=ret_type,
            docstring=doc,
            calls=list(set(call_visitor.calls)),
            is_method=is_method,
            class_name=class_name,
            is_route=is_route,
            route_path=route_path,
            route_method=route_method
        )

    def _parse_class(self, node: ast.ClassDef, file_path: str) -> ClassSymbol:
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(f"{ast.unparse(b.value)}.{b.attr}" if hasattr(ast, "unparse") else b.attr)

        methods = [
            m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        return ClassSymbol(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            methods=methods,
            base_classes=bases
        )

    def _extract_class_methods(self, class_node: ast.ClassDef, file_path: str, class_name: str) -> dict[str, FunctionSymbol]:
        methods = {}
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._parse_function(item, file_path, is_method=True, class_name=class_name)
                methods[fn.qualified_name] = fn
        return methods

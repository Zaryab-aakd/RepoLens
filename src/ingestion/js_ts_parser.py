"""JavaScript and TypeScript AST and symbol extractor."""

import re
from pathlib import Path
from src.ingestion.base import BaseASTParser
from src.models import ClassSymbol, FileSymbols, FunctionSymbol, ImportSymbol


class JavaScriptTypeScriptParser(BaseASTParser):
    """Extracts classes, functions, routes, and imports from JS/TS code using regex & lexical patterns."""

    FUNCTION_DEF_REGEX = re.compile(
        r'(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_$]+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    ARROW_FN_REGEX = re.compile(
        r'(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>',
        re.MULTILINE
    )
    CLASS_DEF_REGEX = re.compile(
        r'(?:export\s+)?class\s+([a-zA-Z0-9_$]+)(?:\s+extends\s+([a-zA-Z0-9_$]+))?',
        re.MULTILINE
    )
    METHOD_DEF_REGEX = re.compile(
        r'^\s*(?:async\s+)?([a-zA-Z0-9_$]+)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )
    IMPORT_ES6_REGEX = re.compile(
        r'import\s+(?:\{([^}]+)\}|([a-zA-Z0-9_$]+))\s+from\s+[\'"]([^\'"]+)[\'"]',
        re.MULTILINE
    )
    IMPORT_CJS_REGEX = re.compile(
        r'(?:const|let|var)\s+(?:\{([^}]+)\}|([a-zA-Z0-9_$]+))\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
        re.MULTILINE
    )
    ROUTE_REGEX = re.compile(
        r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        re.MULTILINE | re.IGNORECASE
    )

    def parse_file(self, file_path: Path, relative_to: Path) -> FileSymbols:
        rel_str = str(file_path.relative_to(relative_to)).replace("\\", "/")
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return FileSymbols(file_path=rel_str, language="typescript" if file_path.suffix.endswith("ts") else "javascript")

        loc = len([line for line in content.splitlines() if line.strip() and not line.strip().startswith("//")])
        symbols = FileSymbols(
            file_path=rel_str,
            language="typescript" if file_path.suffix.endswith("ts") else "javascript",
            loc=loc
        )

        # 1. Imports
        for match in self.IMPORT_ES6_REGEX.finditer(content):
            names_group = match.group(1) or match.group(2)
            names = [n.strip() for n in names_group.split(",") if n.strip()]
            mod = match.group(3)
            symbols.imports.append(
                ImportSymbol(module=mod, imported_names=names, is_relative=mod.startswith("."), file_path=rel_str)
            )
        for match in self.IMPORT_CJS_REGEX.finditer(content):
            names_group = match.group(1) or match.group(2)
            names = [n.strip() for n in names_group.split(",") if n.strip()]
            mod = match.group(3)
            symbols.imports.append(
                ImportSymbol(module=mod, imported_names=names, is_relative=mod.startswith("."), file_path=rel_str)
            )

        # 2. Functions
        for match in self.FUNCTION_DEF_REGEX.finditer(content):
            name = match.group(1)
            raw_args = match.group(2)
            args = [a.split(":")[0].strip() for a in raw_args.split(",") if a.strip()]
            symbols.functions[name] = FunctionSymbol(
                name=name,
                file_path=rel_str,
                arguments=args
            )

        for match in self.ARROW_FN_REGEX.finditer(content):
            name = match.group(1)
            raw_args = match.group(2)
            args = [a.split(":")[0].strip() for a in raw_args.split(",") if a.strip()]
            symbols.functions[name] = FunctionSymbol(
                name=name,
                file_path=rel_str,
                arguments=args
            )

        # 3. Classes
        for match in self.CLASS_DEF_REGEX.finditer(content):
            name = match.group(1)
            base = [match.group(2)] if match.group(2) else []
            symbols.classes[name] = ClassSymbol(
                name=name,
                file_path=rel_str,
                base_classes=base
            )

        # 4. REST Routes
        for match in self.ROUTE_REGEX.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            route_name = f"{method}_{route_path.replace('/', '_').strip('_') or 'root'}"
            symbols.functions[route_name] = FunctionSymbol(
                name=route_name,
                file_path=rel_str,
                is_route=True,
                route_path=route_path,
                route_method=method
            )

        return symbols

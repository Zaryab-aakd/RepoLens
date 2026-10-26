"""Cross-file dependency and module topology matrix builder using NetworkX."""

from typing import Dict, List, Set, Tuple
import networkx as nx
from src.models import RepositoryAST


class DependencyGraphBuilder:
    """Builds explicit module dependency and call graphs addressing Gap 1."""

    def __init__(self, repo_ast: RepositoryAST):
        self.repo_ast = repo_ast
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        # 1. Add all files as nodes
        for file_path, file_sym in self.repo_ast.files.items():
            self.graph.add_node(
                file_path,
                type="module",
                language=file_sym.language,
                loc=file_sym.loc,
                num_classes=len(file_sym.classes),
                num_functions=len(file_sym.functions)
            )

        # 2. Add import edges between files
        all_files = list(self.repo_ast.files.keys())
        for file_path, file_sym in self.repo_ast.files.items():
            for imp in file_sym.imports:
                target_file = self._resolve_import_to_file(imp.module, all_files, file_path)
                if target_file and target_file != file_path:
                    self.graph.add_edge(
                        file_path,
                        target_file,
                        relation="imports",
                        symbols=imp.imported_names
                    )

        # 3. Add function call edges across modules
        symbol_owner: Dict[str, str] = {}
        for file_path, file_sym in self.repo_ast.files.items():
            for fn_name in file_sym.functions.keys():
                symbol_owner[fn_name] = file_path

        for file_path, file_sym in self.repo_ast.files.items():
            for fn in file_sym.functions.values():
                for called in fn.calls:
                    if called in symbol_owner and symbol_owner[called] != file_path:
                        target = symbol_owner[called]
                        if not self.graph.has_edge(file_path, target):
                            self.graph.add_edge(file_path, target, relation="calls", symbols=[called])
                        else:
                            edge_data = self.graph.get_edge_data(file_path, target)
                            if "calls" not in edge_data.get("relation", ""):
                                edge_data["symbols"].append(called)

    def _resolve_import_to_file(self, module_name: str, all_files: List[str], current_file: str) -> str | None:
        if not module_name:
            return None
        # Convert dotted module to path (e.g., utils.helpers -> utils/helpers)
        clean_mod = module_name.strip(".").replace(".", "/")
        for f in all_files:
            stem = f.rsplit(".", 1)[0]
            if stem.endswith(clean_mod) or stem == clean_mod:
                return f
        # Direct basename match
        base_name = module_name.split(".")[-1]
        for f in all_files:
            if f.rsplit(".", 1)[0].split("/")[-1] == base_name:
                return f
        return None

    def get_topology_matrix(self) -> Dict[str, List[str]]:
        """Returns adjacency list of modules."""
        matrix: Dict[str, List[str]] = {}
        for node in self.graph.nodes:
            matrix[node] = list(self.graph.successors(node))
        return matrix

    def get_edge_list(self) -> List[Tuple[str, str]]:
        """Returns list of (source, target) module edges."""
        return list(self.graph.edges())

    def get_summary_metrics(self) -> Dict[str, float]:
        """Calculates graph metrics: node count, edge count, density, cyclicity."""
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = nx.density(self.graph) if num_nodes > 1 else 0.0
        is_dag = nx.is_directed_acyclic_graph(self.graph)
        return {
            "num_nodes": float(num_nodes),
            "num_edges": float(num_edges),
            "density": round(float(density), 4),
            "is_acyclic": 1.0 if is_dag else 0.0
        }

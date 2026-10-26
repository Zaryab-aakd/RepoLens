"""Scanner Agent: Maps codebase structure, extracts AST symbols, and builds dependency matrices."""

from pathlib import Path
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.config import SystemConfig
from src.graph.dependency_graph import DependencyGraphBuilder
from src.ingestion.extractor import RepositoryExtractor
from src.logger import TrajectoryLogger
from src.models import RepositoryAST


class ScannerAgent(BaseAgent):
    """Scanner Agent addressing Gap 1: Context Fragmentation & Topology Loss."""

    def __init__(self, config: SystemConfig, logger: TrajectoryLogger):
        super().__init__("ScannerAgent", config, logger)
        self.extractor = RepositoryExtractor()

    def scan(self, repo_path: Path, repo_name: str) -> Dict[str, Any]:
        self.log(
            action="scan_repository",
            thought=f"Initiating full AST extraction on repository '{repo_name}' located at {repo_path}.",
            input_payload={"repo_path": str(repo_path), "repo_name": repo_name}
        )

        # 1. Parse repository into AST symbol table
        repo_ast: RepositoryAST = self.extractor.extract(repo_path, repo_name=repo_name)

        # 2. Build dependency graph (or degraded topology if ablated)
        if self.config.ablation.enable_scanner_matrix:
            self.log(
                action="build_dependency_matrix",
                thought="Constructing multi-file cross-module dependency and call graph matrix using AST static links."
            )
            graph_builder = DependencyGraphBuilder(repo_ast)
            topology_matrix = graph_builder.get_topology_matrix()
            graph_metrics = graph_builder.get_summary_metrics()
        else:
            self.log(
                action="skip_dependency_matrix (Ablation)",
                thought="Ablation mode active: disabling multi-agent cross-file dependency synthesis. Files analyzed in isolation."
            )
            graph_builder = None
            topology_matrix = {f: [] for f in repo_ast.files.keys()}
            graph_metrics = {"num_nodes": float(len(repo_ast.files)), "num_edges": 0.0, "density": 0.0, "is_acyclic": 1.0}

        scan_result = {
            "repo_ast": repo_ast,
            "graph_builder": graph_builder,
            "topology_matrix": topology_matrix,
            "graph_metrics": graph_metrics,
            "total_files": len(repo_ast.files),
            "total_loc": repo_ast.total_loc,
            "total_functions": len(repo_ast.get_all_function_names()),
            "total_classes": len(repo_ast.get_all_classes())
        }

        self.log(
            action="scan_completed",
            thought=f"Extracted {scan_result['total_files']} files, {scan_result['total_loc']} LOC, "
                    f"{scan_result['total_classes']} classes, {scan_result['total_functions']} functions.",
            output_payload={
                "total_files": scan_result["total_files"],
                "total_loc": scan_result["total_loc"],
                "graph_edges": graph_metrics.get("num_edges", 0)
            }
        )
        return scan_result

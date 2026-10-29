"""Extracts ground-truth symbol tables and topological references for all 10 benchmarks."""

import json
from pathlib import Path
from src.ingestion.extractor import RepositoryExtractor
from src.graph.dependency_graph import DependencyGraphBuilder


def generate_ground_truth():
    benchmarks_dir = Path(__file__).resolve().parent / "benchmarks"
    gt_dir = Path(__file__).resolve().parent / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)

    extractor = RepositoryExtractor()
    topologies = {}
    signatures = {}

    for repo_dir in sorted(benchmarks_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        repo_name = repo_dir.name
        repo_ast = extractor.extract(repo_dir, repo_name)
        builder = DependencyGraphBuilder(repo_ast)

        # 1. Topologies
        nodes = list(repo_ast.files.keys())
        edges = builder.get_edge_list()
        topologies[repo_name] = {
            "nodes": nodes,
            "edges": edges,
            "metrics": builder.get_summary_metrics()
        }

        # 2. Signatures
        sig_map = {}
        for f_name, f_sym in repo_ast.files.items():
            for fn in f_sym.functions.values():
                sig_map[fn.name] = {
                    "file_path": fn.file_path,
                    "arguments": fn.arguments,
                    "is_route": fn.is_route,
                    "route_path": fn.route_path,
                    "route_method": fn.route_method
                }
        signatures[repo_name] = sig_map

    (gt_dir / "ground_truth_topologies.json").write_text(json.dumps(topologies, indent=2), encoding="utf-8")
    (gt_dir / "ground_truth_signatures.json").write_text(json.dumps(signatures, indent=2), encoding="utf-8")
    print("Ground truth topologies and signatures successfully generated!")


if __name__ == "__main__":
    generate_ground_truth()

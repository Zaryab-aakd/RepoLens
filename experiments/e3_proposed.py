"""E3: Proposed System (RepoLens) end-to-end evaluation across all 10 benchmarks."""

import json
from pathlib import Path
from typing import Dict, Any
from src.config import SystemConfig
from src.evaluation.metrics import compute_graph_edit_distance
from src.graph.mermaid_generator import MermaidDiagramGenerator
from src.pipeline.orchestrator import RepoLensOrchestrator


def run_e3_proposed() -> Dict[str, Any]:
    benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"
    gt_dir = Path(__file__).resolve().parent.parent / "data" / "ground_truth"
    results_dir = Path(__file__).resolve().parent.parent / "results" / "tables"
    results_dir.mkdir(parents=True, exist_ok=True)

    gt_topologies = json.loads((gt_dir / "ground_truth_topologies.json").read_text(encoding="utf-8"))

    config = SystemConfig()
    orchestrator = RepoLensOrchestrator(config)
    repo_results = []

    for repo_dir in sorted(benchmarks_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        repo_name = repo_dir.name
        gt_topo = gt_topologies[repo_name]

        # Execute complete RepoLens pipeline
        output = orchestrator.run(repo_dir, repo_name)
        report = output.verification_report

        # Extract generated Mermaid nodes and edges to compute GED against ground truth
        gen_nodes = MermaidDiagramGenerator.parse_mermaid_nodes(output.mermaid_diagram)
        gen_edges = MermaidDiagramGenerator.parse_mermaid_edges(output.mermaid_diagram)

        gt_nodes = set(MermaidDiagramGenerator._sanitize_id(n) for n in gt_topo["nodes"])
        gt_edges = [(MermaidDiagramGenerator._sanitize_id(s), MermaidDiagramGenerator._sanitize_id(d)) for s, d in gt_topo["edges"]]

        ged_data = compute_graph_edit_distance(gen_nodes, gt_nodes, gen_edges, gt_edges)

        repo_results.append({
            "repo_name": repo_name,
            "system": "E3_RepoLens_Proposed",
            "total_claims": report.total_claims,
            "hallucinations": report.total_hallucinations,
            "hallucination_rate": report.hallucination_rate,
            "precision": report.precision,
            "recall": report.recall,
            "ged": ged_data["raw_ged"],
            "edge_precision": ged_data["edge_precision"],
            "edge_recall": ged_data["edge_recall"],
            "iterations_used": output.iterations_used,
            "duration_seconds": output.trajectory.duration_seconds
        })

    avg_hr = round(sum(r["hallucination_rate"] for r in repo_results) / len(repo_results), 4)
    avg_ged = round(sum(r["ged"] for r in repo_results) / len(repo_results), 2)
    avg_prec = round(sum(r["precision"] for r in repo_results) / len(repo_results), 4)
    avg_rec = round(sum(r["recall"] for r in repo_results) / len(repo_results), 4)
    avg_duration = round(sum(r["duration_seconds"] for r in repo_results) / len(repo_results), 4)

    output = {
        "experiment": "E3_Proposed_RepoLens",
        "description": "Complete RepoLens agentic system with AST verification and topological grounding",
        "average_hallucination_rate": avg_hr,
        "average_ged": avg_ged,
        "average_precision": avg_prec,
        "average_recall": avg_rec,
        "average_duration_seconds": avg_duration,
        "repositories": repo_results
    }

    out_file = results_dir / "e3_proposed_results.json"
    out_file.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"[E3 Proposed RepoLens] Completed: Avg HR={avg_hr:.2%}, Avg GED={avg_ged}, Avg Precision={avg_prec:.2%}")
    return output


if __name__ == "__main__":
    run_e3_proposed()

"""Evaluation metrics for RepoLens: Hallucination Rate (HR) and Graph Edit Distance (GED)."""

from typing import Dict, List, Set, Tuple
import networkx as nx


def calculate_hallucination_rate(total_claims: int, hallucinations: int) -> float:
    """Calculates Hallucination Rate (HR) = Hallucinations / Total Claims."""
    if total_claims <= 0:
        return 0.0
    return round(float(hallucinations) / float(total_claims), 4)


def compute_graph_edit_distance(
    gen_nodes: Set[str],
    gt_nodes: Set[str],
    gen_edges: List[Tuple[str, str]],
    gt_edges: List[Tuple[str, str]]
) -> Dict[str, float]:
    """
    Computes Graph Edit Distance (GED) and topological accuracy.
    GED = |node_insertions| + |node_deletions| + |edge_insertions| + |edge_deletions|.
    """
    node_insertions = len(gen_nodes - gt_nodes)
    node_deletions = len(gt_nodes - gen_nodes)

    gen_edge_set = set(gen_edges)
    gt_edge_set = set(gt_edges)

    edge_insertions = len(gen_edge_set - gt_edge_set)
    edge_deletions = len(gt_edge_set - gen_edge_set)

    raw_ged = node_insertions + node_deletions + edge_insertions + edge_deletions

    # Normalized topological F1
    common_nodes = len(gen_nodes.intersection(gt_nodes))
    node_precision = common_nodes / len(gen_nodes) if gen_nodes else 1.0
    node_recall = common_nodes / len(gt_nodes) if gt_nodes else 1.0

    common_edges = len(gen_edge_set.intersection(gt_edge_set))
    edge_precision = common_edges / len(gen_edge_set) if gen_edge_set else 1.0
    edge_recall = common_edges / len(gt_edge_set) if gt_edge_set else 1.0

    return {
        "raw_ged": float(raw_ged),
        "node_insertions": float(node_insertions),
        "node_deletions": float(node_deletions),
        "edge_insertions": float(edge_insertions),
        "edge_deletions": float(edge_deletions),
        "node_precision": round(node_precision, 4),
        "node_recall": round(node_recall, 4),
        "edge_precision": round(edge_precision, 4),
        "edge_recall": round(edge_recall, 4)
    }

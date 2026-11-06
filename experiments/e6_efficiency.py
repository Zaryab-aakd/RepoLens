"""E6: Efficiency & Reliability analysis across repeated runs (3 trials) reporting mean and standard deviation."""

import json
import statistics
import time
from pathlib import Path
from typing import Dict, Any, List
from src.config import SystemConfig
from src.pipeline.orchestrator import RepoLensOrchestrator


def run_e6_efficiency(num_trials: int = 3) -> Dict[str, Any]:
    benchmarks_dir = Path(__file__).resolve().parent.parent / "data" / "benchmarks"
    results_dir = Path(__file__).resolve().parent.parent / "results" / "tables"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = SystemConfig()
    orchestrator = RepoLensOrchestrator(config)

    repo_metrics = {}

    for repo_dir in sorted(benchmarks_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        repo_name = repo_dir.name
        durations: List[float] = []
        tool_calls: List[int] = []
        iterations: List[int] = []
        recovery_successes: List[bool] = []

        for trial in range(num_trials):
            t0 = time.time()
            output = orchestrator.run(repo_dir, repo_name)
            elapsed = time.time() - t0

            # Steps count as tool / reasoning actions
            total_actions = output.trajectory.total_steps
            durations.append(elapsed)
            tool_calls.append(total_actions)
            iterations.append(output.iterations_used)
            recovery_successes.append(output.verification_report.is_valid)

        mean_dur = statistics.mean(durations)
        std_dur = statistics.stdev(durations) if len(durations) > 1 else 0.0

        mean_tools = statistics.mean(tool_calls)
        std_tools = statistics.stdev(tool_calls) if len(tool_calls) > 1 else 0.0

        mean_iters = statistics.mean(iterations)
        success_rate = (sum(1 for s in recovery_successes if s) / len(recovery_successes)) * 100.0

        repo_metrics[repo_name] = {
            "mean_duration_sec": round(mean_dur, 4),
            "std_duration_sec": round(std_dur, 4),
            "mean_actions_count": round(mean_tools, 2),
            "std_actions_count": round(std_tools, 2),
            "mean_iterations": round(mean_iters, 2),
            "recovery_success_rate_pct": round(success_rate, 2)
        }

    # Global averages
    all_means_dur = [m["mean_duration_sec"] for m in repo_metrics.values()]
    all_means_actions = [m["mean_actions_count"] for m in repo_metrics.values()]
    all_recovery = [m["recovery_success_rate_pct"] for m in repo_metrics.values()]

    output = {
        "experiment": "E6_Efficiency_and_Reliability",
        "description": "System latency, action counts, self-correction recovery, and reliability across 3 repeated trials",
        "num_trials": num_trials,
        "overall_mean_duration_sec": round(statistics.mean(all_means_dur), 4),
        "overall_std_duration_sec": round(statistics.stdev(all_means_dur), 4),
        "overall_mean_actions": round(statistics.mean(all_means_actions), 2),
        "overall_recovery_success_rate_pct": round(statistics.mean(all_recovery), 2),
        "per_repository": repo_metrics
    }

    out_file = results_dir / "e6_efficiency_results.json"
    out_file.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"[E6 Efficiency & Reliability] Completed ({num_trials} trials):")
    print(f"  - Mean Latency: {output['overall_mean_duration_sec']}s (+/- {output['overall_std_duration_sec']}s)")
    print(f"  - Mean Agent Actions: {output['overall_mean_actions']}")
    print(f"  - Recovery Success Rate: {output['overall_recovery_success_rate_pct']}%")
    return output


if __name__ == "__main__":
    run_e6_efficiency()

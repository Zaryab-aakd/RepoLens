"""Trajectory and observability logging for RepoLens."""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from src.models import AgentTrajectory, TrajectoryStep


class TrajectoryLogger:
    """Records and persists observable multi-agent reasoning steps and tool calls."""

    def __init__(self, repo_name: str, logs_dir: Optional[Path] = None):
        self.repo_name = repo_name
        self.logs_dir = logs_dir or (Path(__file__).resolve().parent.parent / "logs" / "trajectories")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.trajectory = AgentTrajectory(repo_name=repo_name)
        self._start_time = time.time()
        self._step_counter = 0

    def log_step(
        self,
        agent_role: str,
        action: str,
        thought: str,
        input_payload: Optional[Dict[str, Any]] = None,
        output_payload: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> TrajectoryStep:
        self._step_counter += 1
        step = TrajectoryStep(
            step_id=self._step_counter,
            agent_role=agent_role,
            action=action,
            thought=thought,
            input_payload=input_payload or {},
            output_payload=output_payload or {},
            timestamp=time.time() - self._start_time,
            error=error
        )
        self.trajectory.steps.append(step)
        self.trajectory.total_steps = len(self.trajectory.steps)
        return step

    def record_correction_iteration(self):
        self.trajectory.correction_iterations += 1

    def finalize(self) -> AgentTrajectory:
        self.trajectory.duration_seconds = round(time.time() - self._start_time, 4)
        self.trajectory.total_steps = len(self.trajectory.steps)
        self.save_to_disk()
        return self.trajectory

    def save_to_disk(self, filename: Optional[str] = None) -> Path:
        if not filename:
            filename = f"trajectory_{self.repo_name}.json"
        out_path = self.logs_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.trajectory.model_dump(), f, indent=2)
        return out_path

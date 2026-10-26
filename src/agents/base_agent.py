"""Base agent class with trajectory logging and prompt interface."""

from abc import ABC
from typing import Any, Dict, Optional
from src.config import SystemConfig
from src.logger import TrajectoryLogger


class BaseAgent(ABC):
    """Abstract base agent providing logging and execution context."""

    def __init__(self, role_name: str, config: SystemConfig, logger: TrajectoryLogger):
        self.role_name = role_name
        self.config = config
        self.logger = logger

    def log(
        self,
        action: str,
        thought: str,
        input_payload: Optional[Dict[str, Any]] = None,
        output_payload: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        return self.logger.log_step(
            agent_role=self.role_name,
            action=action,
            thought=thought,
            input_payload=input_payload,
            output_payload=output_payload,
            error=error
        )

"""Task models."""
from typing import List, Callable

class Task:
    def __init__(self, task_id: str, action: Callable, dependencies: List[str] = None):
        self.task_id = task_id
        self.action = action
        self.dependencies = dependencies or []
        self.completed = False

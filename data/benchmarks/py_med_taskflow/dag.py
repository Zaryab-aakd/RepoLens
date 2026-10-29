"""DAG topological scheduler."""
from models import Task
from typing import Dict, List

class TaskDAG:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task):
        self.tasks[task.task_id] = task

    def get_execution_order(self) -> List[str]:
        visited = set()
        order = []
        def dfs(t_id):
            if t_id in visited:
                return
            visited.add(t_id)
            for dep in self.tasks[t_id].dependencies:
                dfs(dep)
            order.append(t_id)
        for t_id in self.tasks:
            dfs(t_id)
        return order

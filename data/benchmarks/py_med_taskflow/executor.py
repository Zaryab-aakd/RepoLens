"""Worker executor pool."""
from dag import TaskDAG

class TaskExecutor:
    def __init__(self, dag: TaskDAG):
        self.dag = dag

    def execute_all(self) -> int:
        order = self.dag.get_execution_order()
        count = 0
        for t_id in order:
            task = self.dag.tasks[t_id]
            task.action()
            task.completed = True
            count += 1
        return count

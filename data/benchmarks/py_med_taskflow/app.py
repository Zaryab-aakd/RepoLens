"""Taskflow application runner."""
from models import Task
from dag import TaskDAG
from executor import TaskExecutor

def build_sample_pipeline() -> int:
    dag = TaskDAG()
    dag.add_task(Task("step1", lambda: print("1")))
    dag.add_task(Task("step2", lambda: print("2"), dependencies=["step1"]))
    executor = TaskExecutor(dag)
    return executor.execute_all()

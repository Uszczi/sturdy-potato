"""Task use cases: one module per operation.

Classes are re-exported here so callers (e.g. the DI composition root) can import
them from ``use_cases.tasks`` without depending on the per-operation module paths.
"""

from use_cases.tasks.count_tasks import CountTasks
from use_cases.tasks.create_task import CreateTask
from use_cases.tasks.delete_task import DeleteTask
from use_cases.tasks.get_task import GetTask
from use_cases.tasks.list_open_tasks import ListOpenTasks
from use_cases.tasks.list_tasks import ListTasks
from use_cases.tasks.move_task import MoveTask
from use_cases.tasks.update_task import UpdateTask
from use_cases.tasks.view_tasks import ViewTasks

__all__ = [
    "CountTasks",
    "CreateTask",
    "DeleteTask",
    "GetTask",
    "ListOpenTasks",
    "ListTasks",
    "MoveTask",
    "UpdateTask",
    "ViewTasks",
]

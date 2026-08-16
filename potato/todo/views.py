from api.views import TodoViewSet
from web.views import task_create_page, task_list_page, task_toggle_page

__all__ = [
    "TodoViewSet",
    "task_create_page",
    "task_list_page",
    "task_toggle_page",
]

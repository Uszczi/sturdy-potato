from django.urls import path

from .views import (
    task_assign_project_page,
    task_create_page,
    task_list_page,
    task_toggle_page,
)

urlpatterns = [
    path("", task_list_page, name="task-list-page"),
    path("create/", task_create_page, name="task-create-page"),
    path("<int:pk>/project/", task_assign_project_page, name="task-assign-project"),
    path("<int:pk>/toggle/", task_toggle_page, name="task-toggle"),
]

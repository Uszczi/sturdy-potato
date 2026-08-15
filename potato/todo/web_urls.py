from django.urls import path

from .views import task_list_page, task_toggle_page

urlpatterns = [
    path("", task_list_page, name="task-list-page"),
    path("<int:task_id>/toggle/", task_toggle_page, name="task-toggle"),
]

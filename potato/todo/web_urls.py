from django.urls import path

from .views import task_list_page

urlpatterns = [
    path("", task_list_page, name="task-list-page"),
]

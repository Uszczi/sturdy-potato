from django.urls import path

from .views import project_create_page, project_detail_page, project_list_page

urlpatterns = [
    path("", project_list_page, name="project-list-page"),
    path("create/", project_create_page, name="project-create-page"),
    path("<int:pk>/", project_detail_page, name="project-detail-page"),
]

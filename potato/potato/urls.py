from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/tasks/", include("todo.urls")),
    path("tasks/", include("todo.web_urls")),
    path("admin/", admin.site.urls),
    path("hello-vite/", TemplateView.as_view(template_name="hello_vite.html")),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]

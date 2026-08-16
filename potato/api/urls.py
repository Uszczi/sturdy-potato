from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, TodoViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TodoViewSet, basename="task")

urlpatterns = router.urls

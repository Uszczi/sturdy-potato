from rest_framework.routers import DefaultRouter

from .views import TodoViewSet

router = DefaultRouter()
router.register("tasks", TodoViewSet, basename="task")

urlpatterns = router.urls

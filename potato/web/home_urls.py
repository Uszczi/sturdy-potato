from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import home_page

urlpatterns = [
    path("", login_required(home_page), name="home-page"),
]

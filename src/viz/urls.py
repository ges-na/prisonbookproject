# from django.urls import path
from django.urls import path

from . import views

urlpatterns = [
    path(r"", views.stats, name="stats"),
]

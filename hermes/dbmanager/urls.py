from django.urls import path
from .views import select_database

urlpatterns = [
    path("select_database/", select_database, name="select_database"),
]

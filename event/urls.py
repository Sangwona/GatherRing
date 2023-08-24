from django.urls import path
from . import views

urlpatterns = [
    path("", views.event, name="event"),
    path("create", views.create, name="create_event")
]
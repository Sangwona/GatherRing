from django.urls import path
from . import views

urlpatterns = [
    path("", views.event, name="event"),
    path("create", views.create, name="create_event"),
    path("create/<int:group_id>", views.create_ingroup, name="create_event_ingroup"),
    path("profile/<int:event_id>", views.event_profile, name="event_profile"),
    path("all", views.all, name="all_events"),
]
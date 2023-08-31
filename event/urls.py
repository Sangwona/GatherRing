from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create, name="create_event"),
    path("create/<int:group_id>/", views.create_ingroup, name="create_event_ingroup"),
    path("edit/<int:event_id>/", views.edit, name="edit_event"),
    path("profile/<int:event_id>/", views.event_profile, name="event_profile"),
    path("all/", views.all, name="all_events"),
    path("manage/<int:event_id>/", views.manage_event, name="manage_event"),
    path("toggle_attendance/<int:event_id>/", views.toggle_attendance, name="toggle_event_attendance"),
    path("toggle_request/<int:event_id>/", views.toggle_request, name="toggle_event_request"),
]
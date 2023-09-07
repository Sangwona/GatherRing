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
    path("attendees/<int:event_id>/", views.show_event_attendees, name="show_event_attendees"),
    path("handle_request/<int:request_id>/", views.handle_request, name="handle_event_request"),
    path("change_status/<int:event_id>/", views.change_status_event, name="change_status_event"),
    path("add_photo/<int:event_id>/", views.add_photo, name="add_event_photo"),
    path("is_attendee/<int:event_id>/", views.is_attendee, name="event_is_attendee"),
    path("get_photos/<int:event_id>", views.get_photos, name="get_event_photos"),
    path("delete/<int:event_id>/", views.delete, name="delete_event"),
]
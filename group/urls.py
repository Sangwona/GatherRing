from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.CreateGroupFormWizard.as_view(), name="create_group"),
    path("profile/<int:group_id>/", views.profile, name="group_profile"),
    path("edit/<int:group_id>/", views.edit, name="edit_group"),
    path("manage/<int:group_id>/", views.manage, name = "manage_group"),
    path("all/", views.all, name="all_groups"),
    path("toggle_membership/<int:group_id>/", views.toggle_membership, name="toggle_group_membership"),
    path("toggle_request/<int:group_id>/", views.toggle_request, name="toggle_group_request"),
    path("members/<int:group_id>/", views.show_group_members, name="show_group_members"),
    path("handle_request/<int:request_id>/", views.handle_request, name="handle_group_request"),
    path("delete/<int:group_id>/", views.delete, name="delete_group"),
]
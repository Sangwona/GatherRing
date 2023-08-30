from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.CreateGroupFormWizard.as_view(), name="create_group"),
    path("profile/<int:group_id>/", views.profile, name="group_profile"),
    path("edit/<int:group_id>/", views.edit, name="edit_group"),
    path("manage/<int:group_id>/", views.manage, name = "manage_group"),
    path("all/", views.all, name="all_groups"),
    path("join/<int:group_id>/", views.join_group, name="join_group"),
    path("request/<int:group_id>/", views.create_group_request, name="create_group_request"),
]
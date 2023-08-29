from django.urls import path
from . import views

urlpatterns = [
    path("profile/<int:group_id>/", views.profile, name="group_profile"),
    path("create/", views.CreateGroupFormWizard.as_view(), name="create_group"),
    path("edit/<int:group_id>/", views.edit, name="edit_group"),
    path("all/", views.all, name="all_groups"),
]
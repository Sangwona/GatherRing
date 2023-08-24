from django.urls import path
from . import views

urlpatterns = [
    path("profile/<int:group_id>", views.profile, name="group_profile"),
    path("create", views.CreateGroupFormWizard.as_view(), name="create_group"),
]
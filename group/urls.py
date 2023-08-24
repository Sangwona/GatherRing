from django.urls import path
from . import views

urlpatterns = [
    path("", views.group, name="group"),
    path("create", views.CreateGroupFormWizard.as_view(), name="create_group"),
]
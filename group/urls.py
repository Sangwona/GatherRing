from django.urls import path
from . import views

urlpatterns = [
    path("", views.group, name="group"),
    path("createGroup", views.FormWizardView.as_view(), name="createGroup"),
]
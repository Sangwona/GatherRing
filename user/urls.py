from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/<int:user_id>/", views.profile, name="user_profile"),
    path("edit/<int:user_id>/", views.edit, name="edit_profile"),
    path("group/<int:user_id>/", views.my_group, name="myGroup"),
    path("event/<int:user_id>/", views.my_event, name="myEvent")
]
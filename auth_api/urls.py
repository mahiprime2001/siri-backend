from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login_no_slash"),
    path("login/", views.login_view, name="login"),
    path("refresh", views.refresh_view, name="refresh_no_slash"),
    path("refresh/", views.refresh_view, name="refresh"),
    path("logout", views.logout_view, name="logout_no_slash"),
    path("logout/", views.logout_view, name="logout"),
    path("health", views.health_view, name="health_no_slash"),
    path("health/", views.health_view, name="health"),
]

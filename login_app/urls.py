from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="home"),        # / → login directo
    path("login/", views.login_view, name="login"), # /login → login
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]

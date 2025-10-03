from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("", views.index, name="index"),
]

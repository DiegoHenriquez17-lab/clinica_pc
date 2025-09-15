from django.urls import path
from . import views

app_name = "diagnostico"

urlpatterns = [
    path("asignar/", views.asignar, name="asignar"),
    path("evaluar/", views.evaluar, name="evaluar"),
    path("listado/", views.listado, name="listado"),
]

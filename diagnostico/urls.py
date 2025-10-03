from django.urls import path
from . import views

app_name = "diagnostico"

urlpatterns = [
    path("", views.index, name="index"),
    path("diagnosticar/<int:equipo_id>/", views.index, name="diagnosticar"),
    path("derivacion/", views.derivacion, name="derivacion"),
    path("hardware/", views.hardware, name="hardware"),
    path("software/", views.software, name="software"),
]

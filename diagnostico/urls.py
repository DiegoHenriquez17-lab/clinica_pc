from django.urls import path
from . import views

app_name = "diagnostico"

urlpatterns = [
    path("", views.index, name="index"),
    path("diagnosticar/<int:equipo_id>/", views.index, name="diagnosticar"),
    path("derivacion/", views.derivacion, name="derivacion"),
    path("hardware/", views.hardware, name="hardware"),
    path("software/", views.software, name="software"),
    path("hardware/send_to_software/<int:reparacion_id>/", views.send_hardware_to_software, name="send_hardware_to_software"),
    path("software/send_to_hardware/<int:reparacion_id>/", views.send_software_to_hardware, name="send_software_to_hardware"),
]

from django.urls import path
from . import views

app_name = "entrega"

urlpatterns = [
    path("", views.index, name="index"),
    path("entregar/<int:equipo_id>/", views.entregar, name="entregar"),
    path("send_back_to_hardware/<int:equipo_id>/", views.send_back_to_hardware, name="send_back_to_hardware"),
    path("send_back_to_software/<int:equipo_id>/", views.send_back_to_software, name="send_back_to_software"),
]

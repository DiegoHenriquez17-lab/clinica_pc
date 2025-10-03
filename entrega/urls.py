from django.urls import path
from . import views

app_name = "entrega"

urlpatterns = [
    path("", views.index, name="index"),
    path("entregar/<int:equipo_id>/", views.entregar, name="entregar"),
]

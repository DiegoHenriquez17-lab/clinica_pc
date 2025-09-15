from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("registrar/", views.registrar_equipo, name="registrar"),
    path("listado/", views.listado_equipos, name="listado"),
    path("detalle/<str:nombre>/", views.detalle_equipo, name="detalle"),
]

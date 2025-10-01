from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("registrar/", views.registrar, name="registrar"),
    path("listado/", views.listado, name="listado"),
    path("detalle/<str:nombre>/", views.detalle, name="detalle"),
    path("editar_equipo/<int:pk>/", views.editar_equipo, name="editar_equipo"),
    path("eliminar_equipo/<int:pk>/", views.eliminar_equipo, name="eliminar_equipo"),
    path("clientes/", views.listado_clientes, name="listado_clientes"),
    path("clientes/crear/", views.crear_cliente, name="crear_cliente"),
    path("clientes/editar/<int:pk>/", views.editar_cliente, name="editar_cliente"),
    path("clientes/eliminar/<int:pk>/", views.eliminar_cliente, name="eliminar_cliente"),
    path("estudiantes/", views.listado_estudiantes, name="listado_estudiantes"),
    path("estudiantes/crear/", views.crear_estudiante, name="crear_estudiante"),
    path("estudiantes/editar/<int:pk>/", views.editar_estudiante, name="editar_estudiante"),
    path("estudiantes/eliminar/<int:pk>/", views.eliminar_estudiante, name="eliminar_estudiante"),
]

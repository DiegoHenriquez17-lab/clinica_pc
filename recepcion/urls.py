from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("registrar/", views.registrar, name="registrar"),
    path("listado/", views.listado, name="listado"),
    path("detalle/<str:nombre>/", views.detalle, name="detalle"),
]

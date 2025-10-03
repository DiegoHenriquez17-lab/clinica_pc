from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("", views.index, name="index"),
    path("cliente/<int:cliente_id>/", views.ver_cliente, name="ver_cliente"),
]

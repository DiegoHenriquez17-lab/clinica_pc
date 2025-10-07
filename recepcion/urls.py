from django.urls import path
from . import views

app_name = "recepcion"

urlpatterns = [
    path("", views.index, name="index"),
    path("cliente/<int:cliente_id>/", views.ver_cliente, name="ver_cliente"),
    path("enviar-boleta/<int:equipo_id>/", views.enviar_boleta_email, name="enviar_boleta_email"),
    path("boleta-pdf/<int:equipo_id>/", views.boleta_pdf_view, name="boleta_pdf_view"),
]

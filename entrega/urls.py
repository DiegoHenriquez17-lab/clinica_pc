from django.urls import path
from . import views

app_name = "entrega"

urlpatterns = [
    path("", views.index, name="index"),
    path("entregar/<int:equipo_id>/", views.entregar, name="entregar"),
    path("send_back_to_hardware/<int:equipo_id>/", views.send_back_to_hardware, name="send_back_to_hardware"),
    path("send_back_to_software/<int:equipo_id>/", views.send_back_to_software, name="send_back_to_software"),
    # Confirmación de retiro por tercero
    path("solicitar_confirmacion/<int:equipo_id>/", views.solicitar_confirmacion_retiro_tercero, name="solicitar_confirmacion"),
    path("confirmacion/<uuid:token>/", views.confirmar_retiro_por_token, name="confirmar_retiro_token"),
    path("confirmacion/<uuid:token>/aprobar/", views.confirmar_retiro_aprobar, name="confirmar_retiro_aprobar"),
    path("confirmacion/<uuid:token>/rechazar/", views.confirmar_retiro_rechazar, name="confirmar_retiro_rechazar"),
    # JSON helpers
    path("estado_confirmacion/<int:equipo_id>/", views.estado_confirmacion, name="estado_confirmacion"),
    path("verificar_codigo/<int:equipo_id>/", views.verificar_codigo, name="verificar_codigo"),
]

from django.urls import path
from . import views

app_name = "entrega"

urlpatterns = [
    path("listado/", views.listado_clientes, name="listado"),
    path("verificar/", views.verificar_buscar, name="verificar_buscar"),   # GET con formulario de búsqueda
    path("verificar/<str:nombre>/", views.verificar, name="verificar"),    # detalle por cliente
    path("reporte/<str:nombre>/", views.reporte, name="reporte"),
    path("comprobante/<str:nombre>/", views.comprobante, name="comprobante"),
]

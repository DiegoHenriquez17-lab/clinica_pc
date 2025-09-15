from django.urls import path
from . import views

app_name = "entrega"

urlpatterns = [
    path("", views.listado_clientes, name="listado"),   # 👉 página inicial
    path("verificar/<str:nombre>/", views.verificar, name="verificar"),
    path("reporte/<str:nombre>/", views.reporte, name="reporte"),
    path("comprobante/<str:nombre>/", views.comprobante, name="comprobante"),
]

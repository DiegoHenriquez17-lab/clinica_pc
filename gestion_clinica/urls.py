"""
URL configuration for gestion_clinica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Redirigir /admin/ al nuevo Explorador de Datos y mantener Django Admin en /djadmin/
    path('admin/', views.admin_redirect, name='admin_redirect'),
    path('djadmin/', admin.site.urls),
    path('dashboard/', login_required(views.DashboardView.as_view()), name='dashboard'),
    path('boleta/<int:equipo_id>/', views.generar_boleta, name='generar_boleta'),
    
    # URLs del panel para gestión de equipos (evita conflicto con Django admin)
    path('panel/equipo/<int:equipo_id>/eliminar/', views.eliminar_equipo, name='eliminar_equipo'),
    path('panel/equipo/<int:equipo_id>/actualizar/', views.actualizar_equipo, name='actualizar_equipo'),
    path('panel/cliente/<int:cliente_id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    
    path("recepcion/", include("recepcion.urls")),
    path("diagnostico/", include("diagnostico.urls")),
    path("entrega/", include("entrega.urls")),
    path("", include("login_app.urls")),
    # Explorador de Base de Datos (estilo panel)
    path('panel/db/login/', views.db_login, name='db_login'),
    path('panel/db/', views.db_home, name='db_home'),
    path('panel/db/<str:model_key>/', views.db_model_list, name='db_model_list'),
    path('panel/db/<str:model_key>/<int:pk>/', views.db_model_detail, name='db_model_detail'),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

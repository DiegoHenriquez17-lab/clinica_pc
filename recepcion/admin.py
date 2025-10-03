from django.contrib import admin
from .models import Cliente, Estudiante, Equipo, TrazaEquipo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "rut", "correo", "ciudad", "telefono", "created_at")
	search_fields = ("nombre", "rut", "correo", "ciudad")


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "email")
	search_fields = ("nombre",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
	list_display = ("tipo_equipo", "serial", "cliente", "estado", "created_at")
	search_fields = ("serial", "cliente__nombre", "tipo_equipo")
	list_filter = ("estado", "tipo_equipo", "created_at")
	readonly_fields = ("created_at", "updated_at")


@admin.register(TrazaEquipo)
class TrazaEquipoAdmin(admin.ModelAdmin):
	list_display = ("equipo", "accion", "usuario", "timestamp")
	search_fields = ("equipo__serial", "equipo__cliente__nombre", "descripcion")
	list_filter = ("accion", "timestamp")
	readonly_fields = ("timestamp",)

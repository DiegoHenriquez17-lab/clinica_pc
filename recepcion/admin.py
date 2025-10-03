from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Estudiante, Equipo, TrazaEquipo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "rut", "correo", "ciudad", "telefono", "tiene_carnet", "created_at")
	search_fields = ("nombre", "rut", "correo", "ciudad")
	readonly_fields = ("preview_carnet",)
	
	def tiene_carnet(self, obj):
		if obj.imagen_carnet:
			return format_html('<span style="color: green;">✓ Sí</span>')
		return format_html('<span style="color: red;">✗ No</span>')
	tiene_carnet.short_description = "Carnet"
	
	def preview_carnet(self, obj):
		if obj.imagen_carnet:
			return format_html('<img src="{}" width="200" height="auto" style="border-radius: 8px;" />', obj.imagen_carnet.url)
		return "No hay imagen de carnet"
	preview_carnet.short_description = "Vista previa del carnet"


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

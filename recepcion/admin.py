from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import Cliente, Estudiante, Equipo, TrazaEquipo
from diagnostico.models import Diagnostico
from entrega.models import Entrega


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
	list_select_related = ("cliente",)
	actions = ["exportar_csv"]

	class TrazaInline(admin.TabularInline):
		model = TrazaEquipo
		extra = 0
		readonly_fields = ("usuario", "accion", "descripcion", "timestamp")
		fields = ("usuario", "accion", "descripcion", "timestamp")

	class DiagnosticoInline(admin.StackedInline):
		model = Diagnostico
		extra = 0
		can_delete = False
		fk_name = "equipo"
		readonly_fields = ("cliente", "estudiante", "diagnostico", "area_recomendada", "prioridad", "costo_estimado", "created_at", "updated_at")
		fields = ("cliente", "estudiante", "diagnostico", "area_recomendada", "prioridad", "costo_estimado", "created_at", "updated_at")

	class EntregaInline(admin.StackedInline):
		model = Entrega
		extra = 0
		can_delete = False
		fk_name = "equipo"
		readonly_fields = ("recibido_por", "documento_receptor", "observaciones_entrega", "cliente_satisfecho", "fecha_entrega", "responsable")
		fields = ("recibido_por", "documento_receptor", "observaciones_entrega", "cliente_satisfecho", "fecha_entrega", "responsable")

	inlines = [DiagnosticoInline, EntregaInline, TrazaInline]

	def exportar_csv(self, request, queryset):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="equipos.csv"'
		writer = csv.writer(response)
		writer.writerow(["ID", "Cliente", "Tipo", "Marca", "Modelo", "Serial", "Estado", "Creado"])
		for e in queryset.select_related('cliente'):
			writer.writerow([e.id, e.cliente.nombre if e.cliente else "", e.tipo_equipo, e.marca, e.modelo, e.serial, e.estado, e.created_at])
		return response
	exportar_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(TrazaEquipo)
class TrazaEquipoAdmin(admin.ModelAdmin):
	list_display = ("equipo", "accion", "usuario", "timestamp")
	search_fields = ("equipo__serial", "equipo__cliente__nombre", "descripcion")
	list_filter = ("accion", "timestamp")
	readonly_fields = ("timestamp",)

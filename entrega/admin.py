from django.contrib import admin
# Register your models here.
from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
	list_display = ("diagnostico_cliente", "diagnostico_equipo", "recibido_por", "observaciones_short", "fecha_entrega")
	search_fields = ("diagnostico__cliente__nombre", "recibido_por", "diagnostico__equipo__nombre")
	list_select_related = ("diagnostico", "diagnostico__cliente", "diagnostico__equipo")

	def diagnostico_cliente(self, obj):
		return obj.diagnostico.cliente.nombre if obj.diagnostico and obj.diagnostico.cliente else ""
	diagnostico_cliente.short_description = "Cliente"

	def diagnostico_equipo(self, obj):
		return str(obj.diagnostico.equipo) if obj.diagnostico and obj.diagnostico.equipo else ""
	diagnostico_equipo.short_description = "Equipo"

	def observaciones_short(self, obj):
		text = (obj.observaciones or "")
		return (text[:75] + "…") if len(text) > 75 else text
	observaciones_short.short_description = "Observaciones"

# Register your models here.

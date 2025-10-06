from django.contrib import admin
# Register your models here.
from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
	list_display = ("diagnostico_cliente", "diagnostico_equipo", "recibido_por", "observaciones_short", "fecha_entrega")
	search_fields = ("equipo__diagnostico__cliente__nombre", "recibido_por", "equipo__tipo_equipo")
	list_select_related = ("equipo", "equipo__diagnostico", "equipo__cliente", "responsable")

	def diagnostico_cliente(self, obj):
		return obj.equipo.diagnostico.cliente.nombre if obj.equipo.diagnostico and obj.equipo.diagnostico.cliente else ""
	diagnostico_cliente.short_description = "Cliente"

	def diagnostico_equipo(self, obj):
		return str(obj.equipo) if obj.equipo else ""
	diagnostico_equipo.short_description = "Equipo"

	def observaciones_short(self, obj):
		text = (obj.observaciones_entrega or "")
		return (text[:75] + "…") if len(text) > 75 else text
	observaciones_short.short_description = "Observaciones"

# Register your models here.

from django.contrib import admin
# Register your models here.
from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
	list_display = ("diagnostico", "recibido_por", "fecha_entrega")
	search_fields = ("diagnostico__cliente__nombre", "recibido_por")

# Register your models here.

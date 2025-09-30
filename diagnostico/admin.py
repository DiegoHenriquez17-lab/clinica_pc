from django.contrib import admin
# Register your models here.
from .models import Diagnostico


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
	list_display = ("equipo", "cliente", "estudiante", "created_at")
	search_fields = ("cliente__nombre", "estudiante__nombre", "equipo__serial")

# Register your models here.

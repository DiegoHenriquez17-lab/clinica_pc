from django.contrib import admin
# Register your models here.
from .models import Cliente, Estudiante, Equipo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "rut", "correo", "telefono", "created_at")
	search_fields = ("nombre", "rut", "correo")


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "email")
	search_fields = ("nombre",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
	list_display = ("tipo_equipo", "serial", "cliente", "created_at")
	search_fields = ("serial", "cliente__nombre", "tipo_equipo")

# Register your models here.

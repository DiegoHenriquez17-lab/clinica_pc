from django.contrib import admin
from .models import Materia


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
	list_display = ("title", "unit", "is_published", "created_at")
	list_filter = ("unit", "is_published")
	search_fields = ("title", "summary", "content")

from django.db import models


class Materia(models.Model):
	"""Representa una materia/unidad que puede mostrarse vía API.

	Campos mínimos: título, slug, número de unidad, contenido y metadatos.
	"""
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	unit = models.PositiveIntegerField(default=1)
	summary = models.TextField(blank=True)
	content = models.TextField()
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["unit", "title"]

	def __str__(self) -> str:
		return f"{self.title} (Unidad {self.unit})"

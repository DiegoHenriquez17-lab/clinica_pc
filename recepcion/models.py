from django.db import models


class Cliente(models.Model):
	nombre = models.CharField(max_length=150)
	rut = models.CharField(max_length=12, blank=True, null=True, unique=False)
	correo = models.EmailField(blank=True, null=True)
	telefono = models.CharField(max_length=30, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["nombre"]

	def __str__(self):
		return f"{self.nombre} ({self.rut or 'sin RUT'})"


class Estudiante(models.Model):
	nombre = models.CharField(max_length=150, unique=True)
	email = models.EmailField(blank=True, null=True)

	def __str__(self):
		return self.nombre


class Equipo(models.Model):
	cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="equipos")
	tipo_equipo = models.CharField(max_length=80)
	problema = models.TextField(blank=True)
	serial = models.CharField(max_length=64, blank=True, null=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.tipo_equipo} - {self.serial or self.pk}"

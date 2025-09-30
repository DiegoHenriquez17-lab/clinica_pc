from django.db import models
from recepcion.models import Equipo, Cliente, Estudiante


class Diagnostico(models.Model):
	equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="diagnosticos")
	cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="diagnosticos")
	estudiante = models.ForeignKey(Estudiante, on_delete=models.SET_NULL, null=True, blank=True)
	diagnostico = models.TextField(blank=True)
	observaciones = models.TextField(blank=True)
	solucion = models.TextField(blank=True)
	tipo_solucion = models.CharField(max_length=80, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Diag {self.equipo} ({self.cliente})"

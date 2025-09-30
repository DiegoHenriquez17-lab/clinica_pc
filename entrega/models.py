from django.db import models
from diagnostico.models import Diagnostico


class Entrega(models.Model):
	diagnostico = models.OneToOneField(Diagnostico, on_delete=models.CASCADE, related_name="entrega")
	fecha_entrega = models.DateTimeField(auto_now_add=True)
	recibido_por = models.CharField(max_length=150)
	observaciones = models.TextField(blank=True)

	def __str__(self):
		return f"Entrega {self.diagnostico} - {self.recibido_por} @ {self.fecha_entrega}"

from django.db import models
from django.contrib.auth.models import User
from recepcion.models import Equipo


class Entrega(models.Model):
	equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name="entrega")
	responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="entregas")
	
	# Datos de quien recibe
	recibido_por = models.CharField(max_length=150)
	documento_receptor = models.CharField(max_length=50)  # DNI/Documento de quien recibe
	
	# Datos de entrega
	observaciones_entrega = models.TextField(blank=True, null=True)
	cliente_satisfecho = models.BooleanField(default=True)
	fecha_entrega = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Entrega {self.equipo} - {self.recibido_por}"

	class Meta:
		ordering = ['-fecha_entrega']

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
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


class RetiroTerceroConfirmacion(models.Model):
	"""Confirmación del titular para retiro por tercero"""
	ESTADO_CHOICES = [
		('pendiente', 'Pendiente'),
		('aprobado', 'Aprobado'),
		('rechazado', 'Rechazado'),
		('expirado', 'Expirado'),
	]

	equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name='confirmacion_retiro')
	receptor_nombre = models.CharField(max_length=150)
	receptor_documento = models.CharField(max_length=50)
	token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	codigo = models.CharField(max_length=6)
	estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()
	responded_at = models.DateTimeField(null=True, blank=True)
	responded_from_ip = models.GenericIPAddressField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Confirmación retiro #{self.equipo_id} - {self.estado}"

	@property
	def is_expired(self):
		return timezone.now() > self.expires_at

	def mark_expired_if_needed(self):
		if self.estado == 'pendiente' and self.is_expired:
			self.estado = 'expirado'
			self.responded_at = timezone.now()
			self.save(update_fields=['estado', 'responded_at'])
		return self.estado == 'expirado'

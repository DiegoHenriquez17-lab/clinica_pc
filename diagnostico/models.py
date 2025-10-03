from django.db import models
from django.contrib.auth.models import User
from recepcion.models import Equipo, Cliente, Estudiante


class Diagnostico(models.Model):
	PRIORIDAD_CHOICES = [
		('baja', 'Baja'),
		('media', 'Media'),
		('alta', 'Alta'),
		('urgente', 'Urgente'),
	]
	
	AREA_CHOICES = [
		('hardware', 'Hardware'),
		('software', 'Software'),
	]

	equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name="diagnostico")
	cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="diagnosticos")
	estudiante = models.ForeignKey(Estudiante, on_delete=models.SET_NULL, null=True, blank=True)
	tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="diagnosticos")
	
	# Campos del diagnóstico
	diagnostico = models.TextField()
	area_recomendada = models.CharField(max_length=20, choices=AREA_CHOICES)
	prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
	costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	
	# Campos de seguimiento
	observaciones = models.TextField(blank=True)
	solucion = models.TextField(blank=True)
	tipo_solucion = models.CharField(max_length=80, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Diagnóstico {self.equipo} - {self.get_prioridad_display()}"


class ReparacionHardware(models.Model):
	diagnostico = models.OneToOneField(Diagnostico, on_delete=models.CASCADE, related_name="reparacion_hardware")
	tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reparaciones_hw")
	trabajo_realizado = models.TextField()
	repuestos_utilizados = models.TextField(blank=True, null=True)
	costo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	completado = models.BooleanField(default=False)
	fecha_inicio = models.DateTimeField(auto_now_add=True)
	fecha_completado = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"HW: {self.diagnostico.equipo}"


class ReparacionSoftware(models.Model):
	diagnostico = models.OneToOneField(Diagnostico, on_delete=models.CASCADE, related_name="reparacion_software")
	tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reparaciones_sw")
	trabajo_realizado = models.TextField()
	software_instalado = models.TextField(blank=True, null=True)
	costo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	completado = models.BooleanField(default=False)
	fecha_inicio = models.DateTimeField(auto_now_add=True)
	fecha_completado = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"SW: {self.diagnostico.equipo}"

from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
	nombre = models.CharField(max_length=150)
	rut = models.CharField(max_length=12, blank=True, null=True, unique=False)
	correo = models.EmailField(blank=True, null=True)
	ciudad = models.CharField(max_length=100, blank=True, null=True)
	telefono = models.CharField(max_length=30, blank=True, null=True)
	imagen_carnet = models.ImageField(upload_to='carnets/', blank=True, null=True, help_text="Imagen del carnet del cliente por seguridad")
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
	ESTADO_CHOICES = [
		('recepcion', 'Recepción'),
		('diagnostico', 'Diagnóstico'),
		('hardware', 'Reparación Hardware'),
		('software', 'Reparación Software'),
		('reparacion', 'En Reparación'),
		('despacho', 'Listo para Despacho'),
		('entregado', 'Entregado'),
	]
	
	TIPO_EQUIPO_CHOICES = [
		('Laptop', 'Laptop'),
		('PC Escritorio', 'PC Escritorio'),
		('All-in-One', 'All-in-One'),
		('Tablet', 'Tablet'),
		('Servidor', 'Servidor'),
		('Otro', 'Otro'),
	]

	cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="equipos")
	tipo_equipo = models.CharField(max_length=80, choices=TIPO_EQUIPO_CHOICES)
	marca = models.CharField(max_length=100, blank=True, null=True)
	modelo = models.CharField(max_length=100, blank=True, null=True)
	serial = models.CharField(max_length=64, blank=True, null=True, db_index=True)
	problema = models.TextField(blank=True)
	accesorios = models.JSONField(default=list, blank=True)  # Para almacenar lista de accesorios
	
	# Campos mejorados según feedback del jefe de carrera
	relato_cliente = models.TextField(blank=True, help_text="Relato exacto del cliente sin edición")
	observaciones_recepcionista = models.TextField(blank=True, help_text="Observaciones del recepcionista")
	caja_cliente = models.TextField(blank=True, help_text="Descripción de accesorios/objetos en caja del cliente")
	caja_equipo = models.TextField(blank=True, help_text="Descripción del estado del equipo recibido")
	
	observaciones_adicionales = models.TextField(blank=True, null=True)
	estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recepcion')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.tipo_equipo} - {self.serial or f'#{self.pk}'}"

	def get_estado_display_class(self):
		"""Retorna la clase CSS para el estado"""
		estado_classes = {
			'recepcion': 'status-recepcion',
			'diagnostico': 'status-diagnostico',
			'hardware': 'status-hardware',
			'software': 'status-software',
			'reparacion': 'status-reparacion',
			'despacho': 'status-despacho',
			'entregado': 'status-entregado',
		}
		return estado_classes.get(self.estado, 'status-recepcion')


class TrazaEquipo(models.Model):
	"""Modelo para registrar el camino del equipo en el sistema"""
	ACCION_CHOICES = [
		('ingreso', 'Ingreso al sistema'),
		('diagnostico', 'Enviado a diagnóstico'),
		('hardware', 'Enviado a reparación hardware'),
		('software', 'Enviado a reparación software'),
		('despacho', 'Listo para despacho'),
		('entregado', 'Equipo entregado'),
		('observacion', 'Observación agregada'),
	]
	
	equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="trazas")
	accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
	descripcion = models.TextField()
	usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-timestamp']
	
	def __str__(self):
		return f"{self.equipo} - {self.get_accion_display()} ({self.timestamp.strftime('%d/%m/%Y %H:%M')})"

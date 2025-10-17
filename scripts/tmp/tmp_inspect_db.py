import os
import django
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()
from recepcion.models import Estudiante, Cliente, Equipo
from diagnostico.models import Diagnostico
from entrega.models import Entrega

print('Estudiantes count:', Estudiante.objects.count())
print('Estudiantes list:', list(Estudiante.objects.values_list('nombre', flat=True)))
print('Clientes count:', Cliente.objects.count())
print('Clientes:', list(Cliente.objects.values('id','nombre','rut')))
print('Equipos count:', Equipo.objects.count())
for eq in Equipo.objects.select_related('cliente').all():
    cliente = eq.cliente.nombre if eq.cliente else None
    print('Equipo', eq.pk, eq.tipo_equipo, 'serial=', eq.serial, 'cliente=', cliente)
print('Diagnosticos count:', Diagnostico.objects.count())
print('Entregas count:', Entrega.objects.count())

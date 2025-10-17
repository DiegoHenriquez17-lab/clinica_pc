import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from recepcion.models import Equipo

# simulate session-stored asignacion
eq = Equipo.objects.first()
asign = {'estudiante': 'IVY ANAYA PRADINES GUZMÁN', 'equipo': {'pk': eq.pk}}

# resolve like view
equipo_ref = asign.get('equipo')
equipo = None
if isinstance(equipo_ref, dict):
    if 'pk' in equipo_ref:
        equipo = Equipo.objects.select_related('cliente').filter(pk=equipo_ref['pk']).first()
    elif 'data' in equipo_ref:
        equipo = equipo_ref.get('data')

# build display
display_asig = {'estudiante': asign.get('estudiante'), 'equipo': {'tipo_equipo': '', 'nombre': ''}}
if hasattr(equipo, 'tipo_equipo'):
    display_asig['equipo']['tipo_equipo'] = equipo.tipo_equipo
    display_asig['equipo']['nombre'] = equipo.cliente.nombre if equipo.cliente else ''

print(display_asig)

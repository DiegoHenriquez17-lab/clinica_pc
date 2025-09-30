import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from recepcion.models import Equipo
from diagnostico import views as dv

# pick an equipo from DB
eq = Equipo.objects.first()
print('eq pk', eq.pk)
# simulate session assignment
if eq:
    asign = {'estudiante': 'TEST STUDENT', 'equipo': {'pk': eq.pk}}
    # emulate what evaluar does
    equipo_ref = asign.get('equipo')
    equipo = None
    if isinstance(equipo_ref, dict):
        if 'pk' in equipo_ref:
            equipo = Equipo.objects.select_related('cliente').filter(pk=equipo_ref['pk']).first()
    print('resolved equipo', equipo, getattr(equipo, 'pk', None))
else:
    print('no equipos in DB')

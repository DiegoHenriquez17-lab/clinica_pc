import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from recepcion.models import Equipo
from diagnostico.models import Diagnostico
from recepcion.models import Estudiante
from django.utils import timezone

# pick equipo
eq = Equipo.objects.first()
print('Using equipo', eq)
# ensure estudiante
est, _ = Estudiante.objects.get_or_create(nombre='IVY ANAYA PRADINES GUZMÁN')
print('Estudiante:', est)
# create diag
d = Diagnostico.objects.create(equipo=eq, cliente=eq.cliente, estudiante=est, diagnostico='Prueba', solucion='Reparado', tipo_solucion='correctiva')
print('Created diag id', d.pk)
print('Total diags:', Diagnostico.objects.count())

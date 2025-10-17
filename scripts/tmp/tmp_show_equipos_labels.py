import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from diagnostico.views import _get_estudiantes_list
from recepcion.models import Equipo

# build labels similar to view
labels = []
for eq in Equipo.objects.select_related('cliente').all():
    label = f"{eq.tipo_equipo} — {eq.cliente.nombre if eq.cliente else '—'}"
    labels.append((eq.pk, label))
print('labels:', labels)
print('estudiantes sample:', _get_estudiantes_list()[:3])

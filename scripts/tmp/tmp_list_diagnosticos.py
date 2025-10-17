import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from diagnostico.models import Diagnostico
from recepcion.models import Equipo, Cliente, Estudiante

qs = Diagnostico.objects.select_related('cliente','estudiante','equipo').all()
print('Diagnosticos count:', qs.count())
for d in qs:
    print('ID', d.pk, 'cliente=', getattr(d.cliente,'nombre',None), 'estudiante=', getattr(d.estudiante,'nombre',None), 'equipo=', getattr(d.equipo,'tipo_equipo',None), 'diag=', d.diagnostico)

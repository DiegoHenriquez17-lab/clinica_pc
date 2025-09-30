import os, sys, django, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from django.conf import settings
from diagnostico.models import Diagnostico

def safe_obj(o):
    if isinstance(o, (list, tuple)):
        return [safe_obj(x) for x in o]
    if isinstance(o, dict):
        return {k: safe_obj(v) for k, v in o.items()}
    try:
        return str(o)
    except Exception:
        return repr(o)

print('DATABASES:', json.dumps(safe_obj(settings.DATABASES), indent=2))
engine = settings.DATABASES['default'].get('ENGINE')
name = settings.DATABASES['default'].get('NAME')
print('ENGINE:', engine)
print('NAME:', name)
if engine and 'sqlite' in engine.lower():
    try:
        st = os.stat(name)
        print('DB file exists:', True)
        print('DB size bytes:', st.st_size)
        print('DB mtime:', time.ctime(st.st_mtime))
    except FileNotFoundError:
        print('DB file exists: False')

qs = Diagnostico.objects.select_related('cliente','estudiante','equipo')
print('Diagnosticos count (ORM):', qs.count())
for d in qs:
    print('ID', d.pk, 'cliente=', getattr(d.cliente,'nombre',None), 'estudiante=', getattr(d.estudiante,'nombre',None), 'equipo=', getattr(d.equipo,'tipo_equipo',None), 'diag=', d.diagnostico)

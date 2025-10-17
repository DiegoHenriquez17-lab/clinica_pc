import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gestion_clinica.settings')
import django
django.setup()
from diagnostico.views import _get_estudiantes_list
lst = _get_estudiantes_list()
print('count', len(lst))
print(lst[:8])

import django
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
import django
django.setup()
from recepcion.models import Estudiante

print('Estudiantes count:', Estudiante.objects.count())
for i, name in enumerate(Estudiante.objects.values_list('nombre', flat=True), start=1):
    print(i, name)

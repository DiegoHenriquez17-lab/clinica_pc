import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Eliminar usuarios existentes de prueba
User.objects.filter(username__in=['admin', 'tecnico', 'recepcion', 'tecnico_hardware', 'tecnico_software', 'diagnostico', 'despacho']).delete()
print("Usuarios de prueba eliminados.")

# Crear usuarios de prueba
users_data = [
    {'username': 'admin', 'password': 'admin123', 'email': 'admin@clinicapc.com', 'is_staff': True, 'is_superuser': True, 'groups': ['admin']},
    {'username': 'recepcion', 'password': 'admin123', 'email': 'recepcion@clinicapc.com', 'is_staff': True, 'is_superuser': False, 'groups': ['recepcion']},
    {'username': 'diagnostico', 'password': 'admin123', 'email': 'diagnostico@clinicapc.com', 'is_staff': True, 'is_superuser': False, 'groups': ['diagnostico']},
    {'username': 'tecnico_hardware', 'password': 'admin123', 'email': 'tecnico_hardware@clinicapc.com', 'is_staff': True, 'is_superuser': False, 'groups': ['hardware']},
    {'username': 'tecnico_software', 'password': 'admin123', 'email': 'tecnico_software@clinicapc.com', 'is_staff': True, 'is_superuser': False, 'groups': ['software']},
    {'username': 'despacho', 'password': 'admin123', 'email': 'despacho@clinicapc.com', 'is_staff': True, 'is_superuser': False, 'groups': ['despacho']},
]

for user_data in users_data:
    username = user_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=user_data['password'],
            email=user_data['email']
        )
        user.is_staff = user_data['is_staff']
        user.is_superuser = user_data['is_superuser']
        user.save()
        print(f"Usuario {username} creado exitosamente.")
    else:
        user = User.objects.get(username=username)
        print(f"Usuario {username} ya existe.")
    # Asignar grupos
    user.groups.clear()
    for group_name in user_data.get('groups', []):
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
    user.save()

print("Usuarios de prueba configurados:")
print("- admin / admin123 (Administrador)")
print("- recepcion / admin123 (Recepción)")
print("- diagnostico / admin123 (Diagnóstico)")
print("- tecnico_hardware / admin123 (Técnico Hardware)")
print("- tecnico_software / admin123 (Técnico Software)")
print("- despacho / admin123 (Despacho)")

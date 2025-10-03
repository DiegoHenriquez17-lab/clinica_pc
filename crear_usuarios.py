from django.contrib.auth.models import User

# Crear usuarios de prueba
users_data = [
    {'username': 'admin', 'password': 'admin123', 'email': 'admin@clinicapc.com', 'is_staff': True, 'is_superuser': True},
    {'username': 'tecnico', 'password': 'tecnico123', 'email': 'tecnico@clinicapc.com', 'is_staff': False, 'is_superuser': False},
    {'username': 'recepcion', 'password': 'recepcion123', 'email': 'recepcion@clinicapc.com', 'is_staff': False, 'is_superuser': False},
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
        print(f"Usuario {username} ya existe.")

print("Usuarios de prueba configurados:")
print("- admin / admin123 (Administrador)")
print("- tecnico / tecnico123 (Técnico)")
print("- recepcion / recepcion123 (Recepción)")
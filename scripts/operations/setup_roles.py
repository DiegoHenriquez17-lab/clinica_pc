from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission

# Crear grupos de trabajo
grupos_roles = [
    'recepcion',
    'diagnostico', 
    'hardware',
    'software',
    'despacho'
]

print("Creando grupos de trabajo...")
for grupo_nombre in grupos_roles:
    group, created = Group.objects.get_or_create(name=grupo_nombre)
    if created:
        print(f"✓ Grupo '{grupo_nombre}' creado")
    else:
        print(f"- Grupo '{grupo_nombre}' ya existe")

# Configurar usuarios con sus roles específicos
usuarios_config = [
    {
        'username': 'recepcionista',
        'password': 'recepcion123',
        'email': 'recepcionista@clinicapc.com',
        'grupos': ['recepcion'],
        'es_staff': False,
        'es_admin': False
    },
    {
        'username': 'diagnosticador',
        'password': 'diagnostico123',
        'email': 'diagnostico@clinicapc.com',
        'grupos': ['diagnostico'],
        'es_staff': False,
        'es_admin': False
    },
    {
        'username': 'tecnico_hw',
        'password': 'hardware123',
        'email': 'hardware@clinicapc.com',
        'grupos': ['hardware'],
        'es_staff': False,
        'es_admin': False
    },
    {
        'username': 'tecnico_sw',
        'password': 'software123',
        'email': 'software@clinicapc.com',
        'grupos': ['software'],
        'es_staff': False,
        'es_admin': False
    },
    {
        'username': 'despachador',
        'password': 'despacho123',
        'email': 'despacho@clinicapc.com',
        'grupos': ['despacho'],
        'es_staff': False,
        'es_admin': False
    },
    # Usuarios multi-rol para testing
    {
        'username': 'tecnico_completo',
        'password': 'tecnico123',
        'email': 'tecnico@clinicapc.com',
        'grupos': ['diagnostico', 'hardware', 'software'],
        'es_staff': False,
        'es_admin': False
    }
]

print("\nConfigurando usuarios con roles...")
for user_config in usuarios_config:
    username = user_config['username']
    
    # Crear o actualizar usuario
    user, created = User.objects.get_or_create(username=username)
    
    if created:
        user.set_password(user_config['password'])
        print(f"✓ Usuario '{username}' creado")
    else:
        print(f"- Usuario '{username}' ya existe, actualizando roles...")
    
    # Configurar propiedades del usuario
    user.email = user_config['email']
    user.is_staff = user_config['es_staff']
    user.is_superuser = user_config['es_admin']
    user.save()
    
    # Limpiar grupos anteriores y asignar nuevos
    user.groups.clear()
    for grupo_nombre in user_config['grupos']:
        grupo = Group.objects.get(name=grupo_nombre)
        user.groups.add(grupo)
        print(f"  - Agregado al grupo '{grupo_nombre}'")

# Mantener usuarios originales pero actualizar el admin
print("\nActualizando usuarios existentes...")
try:
    admin_user = User.objects.get(username='admin')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print("✓ Usuario 'admin' configurado como superusuario")
except User.DoesNotExist:
    print("! Usuario 'admin' no encontrado")

# El usuario 'tecnico' original puede ser usado como técnico completo
try:
    tecnico_user = User.objects.get(username='tecnico')
    tecnico_user.groups.clear()
    for grupo in ['diagnostico', 'hardware', 'software']:
        group = Group.objects.get(name=grupo)
        tecnico_user.groups.add(group)
    print("✓ Usuario 'tecnico' configurado con múltiples roles")
except User.DoesNotExist:
    print("! Usuario 'tecnico' no encontrado")

# El usuario 'recepcion' original
try:
    recepcion_user = User.objects.get(username='recepcion')
    recepcion_user.groups.clear()
    group = Group.objects.get(name='recepcion')
    recepcion_user.groups.add(group)
    print("✓ Usuario 'recepcion' configurado para recepción")
except User.DoesNotExist:
    print("! Usuario 'recepcion' no encontrado")

print(f"\n{'='*50}")
print("SISTEMA DE ROLES CONFIGURADO")
print(f"{'='*50}")
print("\n🔐 USUARIOS Y ACCESOS:")
print("\n👑 ADMINISTRADOR (acceso total):")
print("   • admin / admin123")

print("\n👥 USUARIOS POR ROL:")
print("   📥 RECEPCIÓN:")
print("   • recepcion / recepcion123")
print("   • recepcionista / recepcion123")

print("\n   🔬 DIAGNÓSTICO:")
print("   • diagnosticador / diagnostico123")

print("\n   🔧 HARDWARE:")
print("   • tecnico_hw / hardware123")

print("\n   💻 SOFTWARE:")
print("   • tecnico_sw / software123")

print("\n   📦 DESPACHO:")
print("   • despachador / despacho123")

print("\n   🛠️ TÉCNICO COMPLETO (múltiples áreas):")
print("   • tecnico / tecnico123")
print("   • tecnico_completo / tecnico123")

print(f"\n{'='*50}")
print("¡Sistema listo para usar!")
print("Cada usuario solo verá las secciones de su área.")
print(f"{'='*50}")
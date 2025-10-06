from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

def setup_roles():
    # Crear grupos
    grupos = {
        'admin': {
            'permisos': 'all',  # Acceso total
        },
        'recepcion': {
            'permisos': [
                'add_cliente', 'change_cliente', 'view_cliente', 'delete_cliente',
                'add_equipo', 'change_equipo', 'view_equipo', 'delete_equipo',
                'view_dashboard',
            ],
        },
        'tecnico': {
            'permisos': [
                'view_equipo', 'change_equipo',
                'view_diagnostico', 'change_diagnostico',
                'view_hardware', 'change_hardware',
                'view_software', 'change_software',
            ],
        },
        'diagnostico': {
            'permisos': [
                'view_diagnostico', 'change_diagnostico',
                'view_derivacion', 'change_derivacion',
            ],
        },
        'hardware': {
            'permisos': [
                'view_hardware', 'change_hardware',
            ],
        },
        'software': {
            'permisos': [
                'view_software', 'change_software',
            ],
        },
        'despacho': {
            'permisos': [
                'view_despacho', 'change_despacho',
            ],
        },
    }

    # Crear grupos y asignar permisos
    for nombre_grupo, datos in grupos.items():
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if datos['permisos'] == 'all':
            # Asignar todos los permisos
            permisos = Permission.objects.all()
            grupo.permissions.set(permisos)
        else:
            permisos = []
            for codename in datos['permisos']:
                try:
                    permiso = Permission.objects.get(codename=codename)
                    permisos.append(permiso)
                except Permission.DoesNotExist:
                    print(f"Permiso {codename} no encontrado.")
            grupo.permissions.set(permisos)
        grupo.save()
        print(f"Grupo '{nombre_grupo}' configurado con permisos.")

    # Opcional: asignar grupos a usuarios existentes para pruebas
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_user.groups.clear()
        admin_group = Group.objects.get(name='admin')
        admin_user.groups.add(admin_group)
        print("Usuario admin configurado como superusuario y asignado al grupo admin.")

    tecnico_user = User.objects.filter(username='tecnico').first()
    if tecnico_user:
        tecnico_user.is_staff = True
        tecnico_user.is_superuser = False
        tecnico_user.save()
        tecnico_user.groups.clear()
        tecnico_group = Group.objects.get(name='tecnico')
        tecnico_user.groups.add(tecnico_group)
        print("Usuario tecnico asignado al grupo tecnico.")

    recepcion_user = User.objects.filter(username='recepcion').first()
    if recepcion_user:
        recepcion_user.is_staff = True
        recepcion_user.is_superuser = False
        recepcion_user.save()
        recepcion_user.groups.clear()
        recepcion_group = Group.objects.get(name='recepcion')
        recepcion_user.groups.add(recepcion_group)
        print("Usuario recepcion asignado al grupo recepcion.")

if __name__ == '__main__':
    setup_roles()

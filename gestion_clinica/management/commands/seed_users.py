from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


USERS_DATA = [
    {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@clinicapc.com',
        'is_staff': True,
        'is_superuser': True,
        'groups': ['admin'],
    },
    {
        'username': 'recepcion',
        'password': 'admin123',
        'email': 'recepcion@clinicapc.com',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['recepcion'],
    },
    {
        'username': 'diagnostico',
        'password': 'admin123',
        'email': 'diagnostico@clinicapc.com',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['diagnostico'],
    },
    {
        'username': 'tecnico_hardware',
        'password': 'admin123',
        'email': 'tecnico_hardware@clinicapc.com',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['hardware'],
    },
    {
        'username': 'tecnico_software',
        'password': 'admin123',
        'email': 'tecnico_software@clinicapc.com',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['software'],
    },
    {
        'username': 'despacho',
        'password': 'admin123',
        'email': 'despacho@clinicapc.com',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['despacho'],
    },
]


def get_perms_for_model(model, perms=("add", "view", "change", "delete")):
    ct = ContentType.objects.get_for_model(model)
    codename_prefix = model._meta.model_name
    return [
        Permission.objects.get(codename=f"{p}_{codename_prefix}", content_type=ct)
        for p in perms
    ]


class Command(BaseCommand):
    help = "Crea grupos con permisos y usuarios de prueba para Clínica PC"

    def handle(self, *args, **options):
        # Importar modelos localmente para evitar problemas de import
        from recepcion.models import Cliente, Equipo, TrazaEquipo
        from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware
        from entrega.models import Entrega, RetiroTerceroConfirmacion

        # 1) Crear grupos
        group_names = ['admin', 'recepcion', 'diagnostico', 'hardware', 'software', 'despacho']
        groups = {}
        for name in group_names:
            groups[name], _ = Group.objects.get_or_create(name=name)

        # 2) Asignar permisos por grupo
        # Recepción: CRUD sobre Cliente, Equipo, TrazaEquipo
        recepcion_perms = []
        recepcion_perms += get_perms_for_model(Cliente)
        recepcion_perms += get_perms_for_model(Equipo)
        recepcion_perms += get_perms_for_model(TrazaEquipo)
        groups['recepcion'].permissions.set(recepcion_perms)

        # Diagnóstico: CRUD Diagnostico y Traza; ver/cambiar Equipo
        diagnostico_perms = []
        diagnostico_perms += get_perms_for_model(Diagnostico)
        diagnostico_perms += get_perms_for_model(TrazaEquipo)
        diagnostico_perms += get_perms_for_model(Equipo, perms=("view", "change"))
        groups['diagnostico'].permissions.set(diagnostico_perms)

        # Hardware: CRUD ReparacionHardware; ver Equipo y Diagnostico; cambiar Equipo
        hardware_perms = []
        hardware_perms += get_perms_for_model(ReparacionHardware)
        hardware_perms += get_perms_for_model(Equipo, perms=("view", "change"))
        hardware_perms += get_perms_for_model(Diagnostico, perms=("view",))
        groups['hardware'].permissions.set(hardware_perms)

        # Software: CRUD ReparacionSoftware; ver Equipo y Diagnostico; cambiar Equipo
        software_perms = []
        software_perms += get_perms_for_model(ReparacionSoftware)
        software_perms += get_perms_for_model(Equipo, perms=("view", "change"))
        software_perms += get_perms_for_model(Diagnostico, perms=("view",))
        groups['software'].permissions.set(software_perms)

        # Despacho: CRUD Entrega y RetiroTerceroConfirmacion; ver Equipo y Diagnostico
        despacho_perms = []
        despacho_perms += get_perms_for_model(Entrega)
        despacho_perms += get_perms_for_model(RetiroTerceroConfirmacion)
        despacho_perms += get_perms_for_model(Equipo, perms=("view",))
        despacho_perms += get_perms_for_model(Diagnostico, perms=("view",))
        groups['despacho'].permissions.set(despacho_perms)

        # Admin group (informativo); superuser no necesita permisos explícitos
        groups['admin'].permissions.clear()

        # 3) Crear usuarios y asociarlos a grupos
        for u in USERS_DATA:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'is_staff': u['is_staff'],
                    'is_superuser': u['is_superuser'],
                }
            )
            if created:
                user.set_password(u['password'])
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {user.username}"))
            else:
                # Mantener password conocida para entorno demo
                user.set_password(u['password'])
                self.stdout.write(self.style.WARNING(f"Usuario actualizado: {user.username}"))

            user.is_staff = u['is_staff']
            user.is_superuser = u['is_superuser']
            user.email = u['email']
            user.save()

            # Asignar grupos
            user.groups.clear()
            for g in u.get('groups', []):
                user.groups.add(groups[g])
            user.save()

        self.stdout.write(self.style.SUCCESS("Grupos, permisos y usuarios de prueba listos."))

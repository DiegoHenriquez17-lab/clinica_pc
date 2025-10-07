from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Configura los usuarios y roles iniciales para la clínica'

    def handle(self, *args, **options):
        self.stdout.write('Configurando usuarios y roles iniciales...')

        # Crear grupos
        grupos_roles = [
            'recepcion',
            'diagnostico',
            'hardware',
            'software',
            'despacho'
        ]

        self.stdout.write('Creando grupos de trabajo...')
        for grupo_nombre in grupos_roles:
            group, created = Group.objects.get_or_create(name=grupo_nombre)
            if created:
                self.stdout.write(f"✓ Grupo '{grupo_nombre}' creado")
            else:
                self.stdout.write(f"- Grupo '{grupo_nombre}' ya existe")

        # Eliminar usuarios existentes de prueba
        User.objects.filter(username__in=['admin', 'tecnico', 'recepcion', 'tecnico_hardware', 'tecnico_software', 'diagnostico', 'despacho']).delete()
        self.stdout.write("Usuarios de prueba eliminados.")

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
                self.stdout.write(f"Usuario {username} creado exitosamente.")
            else:
                user = User.objects.get(username=username)
                self.stdout.write(f"Usuario {username} ya existe.")
            # Asignar grupos
            user.groups.clear()
            for group_name in user_data.get('groups', []):
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            user.save()



        # Mantener usuarios originales pero actualizar el admin
        self.stdout.write("\nActualizando usuarios existentes...")
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write("✓ Usuario 'admin' configurado como superusuario")
        except User.DoesNotExist:
            self.stdout.write("! Usuario 'admin' no encontrado")

        # El usuario 'tecnico' original puede ser usado como técnico completo
        try:
            tecnico_user = User.objects.get(username='tecnico')
            tecnico_user.groups.clear()
            for grupo in ['diagnostico', 'hardware', 'software']:
                group = Group.objects.get(name=grupo)
                tecnico_user.groups.add(group)
            self.stdout.write("✓ Usuario 'tecnico' configurado con múltiples roles")
        except User.DoesNotExist:
            self.stdout.write("! Usuario 'tecnico' no encontrado")

        # El usuario 'recepcion' original
        try:
            recepcion_user = User.objects.get(username='recepcion')
            recepcion_user.groups.clear()
            group = Group.objects.get(name='recepcion')
            recepcion_user.groups.add(group)
            self.stdout.write("✓ Usuario 'recepcion' configurado para recepción")
        except User.DoesNotExist:
            self.stdout.write("! Usuario 'recepcion' no encontrado")

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("SISTEMA DE ROLES CONFIGURADO")
        self.stdout.write(f"{'='*50}")
        self.stdout.write("\n🔐 USUARIOS Y ACCESOS:")
        self.stdout.write("\n👑 ADMINISTRADOR (acceso total):")
        self.stdout.write("   • admin / admin123")

        self.stdout.write("\n👥 USUARIOS POR ROL:")
        self.stdout.write("   📥 RECEPCIÓN:")
        self.stdout.write("   • recepcion / admin123")

        self.stdout.write("\n   🔬 DIAGNÓSTICO:")
        self.stdout.write("   • diagnostico / admin123")

        self.stdout.write("\n   🔧 HARDWARE:")
        self.stdout.write("   • tecnico_hardware / admin123")

        self.stdout.write("\n   💻 SOFTWARE:")
        self.stdout.write("   • tecnico_software / admin123")

        self.stdout.write("\n   📦 DESPACHO:")
        self.stdout.write("   • despacho / admin123")

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("¡Sistema listo para usar!")
        self.stdout.write("Cada usuario solo verá las secciones de su área.")
        self.stdout.write(f"{'='*50}")

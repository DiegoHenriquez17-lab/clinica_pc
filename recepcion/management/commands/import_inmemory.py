from django.core.management.base import BaseCommand
from recepcion import views as recep_views
from diagnostico import views as diag_views
from entrega import views as entrega_views
from recepcion.models import Cliente, Equipo, Estudiante
from diagnostico.models import Diagnostico
from entrega.models import Entrega
from django.db import transaction

class Command(BaseCommand):
    help = "Importa datos que estaban en listas en memoria hacia la base de datos"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando importación de datos en memoria...")
        with transaction.atomic():
            # Importar estudiantes fijos
            est_names = getattr(recep_views, 'estudiantes', [])
            for name in est_names:
                Estudiante.objects.get_or_create(nombre=name)
            self.stdout.write(f"Estudiantes importados/asegurados: {len(est_names)}")

            # Importar equipos y clientes
            equipos = getattr(recep_views, 'equipos_registrados', [])
            created_clientes = 0
            created_equipos = 0
            for e in equipos:
                nombre = e.get('nombre')
                tipo = e.get('tipo_equipo')
                problema = e.get('problema')
                rut = e.get('rut')
                correo = e.get('correo')
                telefono = e.get('telefono')
                serial = e.get('serial')

                cliente, created = Cliente.objects.get_or_create(nombre=nombre, defaults={'rut': rut, 'correo': correo, 'telefono': telefono})
                if created:
                    created_clientes += 1
                equipo_obj, created = Equipo.objects.get_or_create(cliente=cliente, tipo_equipo=tipo, serial=serial or None, defaults={'problema': problema})
                if created:
                    created_equipos += 1

            self.stdout.write(f"Clientes creados: {created_clientes} | Equipos creados: {created_equipos}")

            # Importar diagnósticos
            diag_list = getattr(diag_views, 'diagnosticos', [])
            created_diags = 0
            for d in diag_list:
                cliente_nombre = d.get('cliente')
                estudiante_nombre = d.get('estudiante')
                equipo_desc = d.get('equipo')
                diagnostico_txt = d.get('diagnostico')
                solucion = d.get('solucion')
                observaciones = d.get('observaciones')

                # intentar enlazar cliente y equipo
                cliente = Cliente.objects.filter(nombre=cliente_nombre).first()
                # equipo: buscar por serial dentro de la descripción si está presente
                equipo = None
                if cliente:
                    equipo = cliente.equipos.first()
                estudiante = None
                if estudiante_nombre:
                    estudiante = Estudiante.objects.filter(nombre=estudiante_nombre).first()

                diag_obj = Diagnostico.objects.create(
                    equipo=equipo,
                    cliente=cliente,
                    estudiante=estudiante,
                    diagnostico=diagnostico_txt or "",
                    solucion=solucion or "",
                    observaciones=observaciones or "",
                )
                created_diags += 1

            self.stdout.write(f"Diagnósticos importados: {created_diags}")

            # Importar entregas (si existieran)
            entregas = getattr(entrega_views, 'entregas', [])
            created_ent = 0
            for ent in entregas:
                nombre = ent.get('nombre')
                estado = ent.get('estado')
                observaciones = ent.get('observaciones')
                # intentar emparejar diagnóstico por cliente
                diag = Diagnostico.objects.filter(cliente__nombre=nombre).first()
                if diag:
                    Entrega.objects.create(diagnostico=diag, recibido_por=nombre, observaciones=observaciones or "")
                    created_ent += 1

            self.stdout.write(f"Entregas importadas: {created_ent}")

        self.stdout.write(self.style.SUCCESS('Importación completa.'))

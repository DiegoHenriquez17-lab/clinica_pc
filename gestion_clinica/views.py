from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recepcion.models import Equipo, TrazaEquipo, Cliente
from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware
from django.utils import timezone
from datetime import timedelta
from recepcion.forms import EquipoForm, ClienteForm
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from functools import wraps


class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener parámetros de filtro desde la URL
        estado_filtro = self.request.GET.get('estado', '')
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')
        ordenar_por = self.request.GET.get('ordenar', '-created_at')
        buscar = self.request.GET.get('buscar', '').strip()
        
        # Estadísticas generales - SINCRONIZADAS
        total_equipos = Equipo.objects.count()
        en_proceso = Equipo.objects.filter(
            estado__in=['diagnostico', 'hardware', 'software', 'reparacion']
        ).count()
        listos = Equipo.objects.filter(estado='despacho').count()
        entregados = Equipo.objects.filter(estado='entregado').count()
        
        context['stats'] = {
            'total': total_equipos,
            'en_proceso': en_proceso,
            'listos': listos,
            'entregados': entregados,
        }
        
        # Aplicar filtros a los equipos
        equipos_query = Equipo.objects.select_related('cliente')
        
        # Filtro de búsqueda
        if buscar:
            from django.db.models import Q
            equipos_query = equipos_query.filter(
                Q(id__icontains=buscar) |
                Q(cliente__nombre__icontains=buscar) |
                Q(cliente__rut__icontains=buscar) |
                Q(tipo_equipo__icontains=buscar) |
                Q(marca__icontains=buscar) |
                Q(modelo__icontains=buscar) |
                Q(serial__icontains=buscar) |
                Q(problema__icontains=buscar) |
                Q(relato_cliente__icontains=buscar)
            )
        
        # Filtro por estado
        if estado_filtro:
            equipos_query = equipos_query.filter(estado=estado_filtro)
        
        # Filtro por rango de fechas
        if fecha_desde:
            try:
                fecha_desde_obj = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                equipos_query = equipos_query.filter(created_at__date__gte=fecha_desde_obj)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                equipos_query = equipos_query.filter(created_at__date__lte=fecha_hasta_obj)
            except ValueError:
                pass
        
        # Aplicar ordenamiento
        if ordenar_por in ['created_at', '-created_at', 'estado', '-estado', 'cliente__nombre', '-cliente__nombre']:
            equipos_query = equipos_query.order_by(ordenar_por)
        else:
            equipos_query = equipos_query.order_by('-created_at')
        
    # Limitar resultados para rendimiento
        context['equipos_recientes'] = equipos_query[:50]
        
        # Agregar opciones de filtro al contexto
        context['filtros'] = {
            'estado_actual': estado_filtro,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'ordenar_actual': ordenar_por,
            'buscar': buscar,
            'estados_disponibles': [
                ('', 'Todos los estados'),
                ('recepcion', 'Recepción'),
                ('diagnostico', 'Diagnóstico'),
                ('hardware', 'Reparación Hardware'),
                ('software', 'Reparación Software'),
                ('despacho', 'Listo para entrega'),
                ('entregado', 'Entregado'),
            ],
            'ordenar_opciones': [
                ('-created_at', 'Más reciente primero'),
                ('created_at', 'Más antiguo primero'),
                ('cliente__nombre', 'Cliente A-Z'),
                ('-cliente__nombre', 'Cliente Z-A'),
                ('estado', 'Estado A-Z'),
                ('-estado', 'Estado Z-A'),
            ]
        }
        
        # Permiso de eliminación (solo admin o grupo 'recepcion')
        user = self.request.user
        context['can_delete'] = (
            user.is_authenticated and (user.is_superuser or user.groups.filter(name='recepcion').exists())
        )

        return context


@login_required
def generar_boleta(request, equipo_id):
    """Generar boleta completa con toda la información del equipo"""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Obtener información relacionada
    diagnostico = None
    reparacion_hardware = None
    reparacion_software = None
    
    try:
        diagnostico = equipo.diagnostico
        if diagnostico.area_recomendada == 'hardware' and hasattr(diagnostico, 'reparacion_hardware'):
            reparacion_hardware = diagnostico.reparacion_hardware
        elif diagnostico.area_recomendada == 'software' and hasattr(diagnostico, 'reparacion_software'):
            reparacion_software = diagnostico.reparacion_software
    except Diagnostico.DoesNotExist:
        pass
    
    # Obtener traza del equipo
    trazas = TrazaEquipo.objects.filter(equipo=equipo).order_by('timestamp')
    
    context = {
        'equipo': equipo,
        'diagnostico': diagnostico,
        'reparacion_hardware': reparacion_hardware,
        'reparacion_software': reparacion_software,
        'trazas': trazas,
    }
    
    return render(request, 'boleta.html', context)


@login_required
def eliminar_equipo(request, equipo_id):
    """Eliminar equipo - Disponible para usuarios con acceso al panel (is_staff)."""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard')
    # Solo admin o grupo 'recepcion' puede eliminar
    if not (request.user.is_superuser or request.user.groups.filter(name='recepcion').exists()):
        messages.error(request, "Solo administradores o recepción pueden eliminar equipos.")
        return redirect('dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        # Confirmar eliminación
        nombre_cliente = equipo.cliente.nombre
        tipo_equipo = equipo.tipo_equipo
        
        # Eliminar el equipo (y sus relaciones por cascada)
        equipo.delete()
        
        messages.success(request, f"Equipo #{equipo_id} de {nombre_cliente} ({tipo_equipo}) ha sido eliminado correctamente.")
        return redirect('dashboard')
    
    # Mostrar confirmación
    context = {
        'equipo': equipo,
        'accion': 'eliminar'
    }
    return render(request, 'admin/confirmar_accion.html', context)


@login_required
def actualizar_equipo(request, equipo_id):
    """Actualizar información del equipo - Disponible para usuarios con acceso al panel (is_staff)."""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        equipo_form = EquipoForm(request.POST, instance=equipo)
        cliente_form = ClienteForm(request.POST, instance=equipo.cliente)

        if equipo_form.is_valid() and cliente_form.is_valid():
            equipo_form.save()
            cliente_form.save()

            # Crear registro en traza (usar una clave válida del choice y detalle en descripcion)
            TrazaEquipo.objects.create(
                equipo=equipo,
                usuario=request.user,
                accion='observacion',
                descripcion=f"Información actualizada por {request.user.username}"
            )

            messages.success(request, f"Equipo #{equipo_id} actualizado correctamente.")
            return redirect('generar_boleta', equipo_id=equipo_id)
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    
    # Mostrar formulario de edición
    # Preparar formularios para GET o para re-render en caso de errores
    if request.method != 'POST':
        equipo_form = EquipoForm(instance=equipo)
        cliente_form = ClienteForm(instance=equipo.cliente)

    context = {
        'equipo': equipo,
        'equipo_form': equipo_form,
        'cliente_form': cliente_form,
    }
    return render(request, 'admin/actualizar_equipo.html', context)


@login_required
def eliminar_cliente(request, cliente_id):
    """Eliminar cliente y sus equipos relacionados.
    Restringido a admin o grupo 'recepcion'.
    """
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard')

    if not (request.user.is_superuser or request.user.groups.filter(name='recepcion').exists()):
        messages.error(request, "Solo administradores o recepción pueden eliminar clientes.")
        return redirect('dashboard')

    cliente = get_object_or_404(Cliente, id=cliente_id)
    equipos_count = cliente.equipos.count()

    if request.method == 'POST':
        nombre = cliente.nombre
        rut = cliente.rut or 'sin RUT'
        cliente.delete()  # CASCADE eliminará equipos asociados
        messages.success(request, f"Cliente '{nombre}' ({rut}) eliminado correctamente. Se eliminaron {equipos_count} equipos asociados.")
        return redirect('dashboard')

    context = {
        'cliente': cliente,
        'equipos_count': equipos_count,
        'accion': 'eliminar_cliente',
    }
    return render(request, 'admin/confirmar_eliminar_cliente.html', context)


# ==============================
# Admin redirect y Explorador DB
# ==============================
@login_required
def admin_redirect(request):
    """Reemplaza /admin/ por el panel/dashboard o el explorador de BD."""
    # Si es staff, lo llevamos al explorador de BD; si no, al dashboard.
    if request.user.is_staff:
        return redirect('db_home')
    return redirect('dashboard')


# =======================
# Protección extra por PIN
# =======================
DB_PIN_SESSION_KEY = 'db_pin_ok'
DB_PIN_VALUE = 'Inacap2025'


def require_db_pin(view_func):
    """Decorator: requiere PIN de Base de Datos almacenado en sesión.
    Se suma al requisito de is_staff ya presente.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("No autorizado")
        if not request.session.get(DB_PIN_SESSION_KEY, False):
            # Guardar destino para volver luego del login PIN
            next_url = request.get_full_path()
            return redirect(f"/panel/db/login/?next={next_url}")
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
def db_login(request):
    """Pequeño login por PIN para acceder a la sección Base de Datos."""
    if not request.user.is_staff:
        return HttpResponseForbidden("No autorizado")

    # Si ya tiene PIN válido en sesión, redirigir a destino
    if request.session.get(DB_PIN_SESSION_KEY, False):
        return redirect(request.GET.get('next') or 'db_home')

    error = None
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        if pin == DB_PIN_VALUE:
            request.session[DB_PIN_SESSION_KEY] = True
            messages.success(request, 'Acceso a Base de Datos concedido.')
            return redirect(request.POST.get('next') or 'db_home')
        else:
            error = 'PIN incorrecto.'

    context = { 'next': request.GET.get('next', '') , 'error': error }
    return render(request, 'db/login.html', context)


def _db_models_config():
    """Mapa de modelos disponibles en el explorador."""
    return {
        'clientes': {
            'model': Cliente,
            'title': 'Clientes',
            'columns': ['id', 'nombre', 'rut', 'correo', 'telefono', 'created_at'],
            'search': ['nombre__icontains', 'rut__icontains', 'correo__icontains', 'telefono__icontains'],
            'default_order': '-id',
        },
        'equipos': {
            'model': Equipo,
            'title': 'Equipos',
            'columns': ['id', 'cliente__nombre', 'tipo_equipo', 'marca', 'modelo', 'serial', 'estado', 'created_at'],
            'search': ['id__icontains', 'cliente__nombre__icontains', 'cliente__rut__icontains', 'tipo_equipo__icontains', 'marca__icontains', 'modelo__icontains', 'serial__icontains', 'problema__icontains'],
            'default_order': '-id',
        },
        'diagnosticos': {
            'model': Diagnostico,
            'title': 'Diagnósticos',
            'columns': ['id', 'equipo__id', 'cliente__nombre', 'area_recomendada', 'prioridad', 'costo_estimado', 'created_at'],
            'search': ['equipo__id__icontains', 'cliente__nombre__icontains', 'prioridad__icontains', 'diagnostico__icontains'],
            'default_order': '-id',
        },
        'hardware': {
            'model': ReparacionHardware,
            'title': 'Reparaciones Hardware',
            'columns': ['id', 'diagnostico__equipo__id', 'diagnostico__cliente__nombre', 'completado', 'costo_final', 'fecha_inicio', 'fecha_completado'],
            'search': ['diagnostico__equipo__id__icontains', 'diagnostico__cliente__nombre__icontains', 'trabajo_realizado__icontains'],
            'default_order': '-id',
        },
        'software': {
            'model': ReparacionSoftware,
            'title': 'Reparaciones Software',
            'columns': ['id', 'diagnostico__equipo__id', 'diagnostico__cliente__nombre', 'completado', 'costo_final', 'fecha_inicio', 'fecha_completado'],
            'search': ['diagnostico__equipo__id__icontains', 'diagnostico__cliente__nombre__icontains', 'trabajo_realizado__icontains', 'software_instalado__icontains'],
            'default_order': '-id',
        },
        'trazas': {
            'model': TrazaEquipo,
            'title': 'Trazabilidad',
            'columns': ['id', 'equipo__id', 'equipo__cliente__nombre', 'accion', 'usuario__username', 'timestamp'],
            'search': ['equipo__id__icontains', 'equipo__cliente__nombre__icontains', 'accion__icontains', 'descripcion__icontains', 'usuario__username__icontains'],
            'default_order': '-id',
        },
    }


@login_required
@require_db_pin
def db_home(request):

    cfg = _db_models_config()
    stats = []
    for key, meta in cfg.items():
        model = meta['model']
        stats.append({
            'key': key,
            'title': meta['title'],
            'count': model.objects.count(),
        })
    context = { 'stats': stats }
    return render(request, 'db/home.html', context)


@login_required
@require_db_pin
def db_model_list(request, model_key):

    cfg = _db_models_config()
    if model_key not in cfg:
        messages.error(request, 'Modelo no disponible')
        return redirect('db_home')

    meta = cfg[model_key]
    model = meta['model']
    columns = meta['columns']

    qs = model.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        q_obj = Q()
        for field in meta['search']:
            q_obj |= Q(**{field: q})
        qs = qs.filter(q_obj)

    order = request.GET.get('order', meta['default_order'])
    # Validación simple de order por seguridad
    if order.lstrip('-') not in [c.split('__')[0] if '__' in c else c for c in columns]:
        order = meta['default_order']
    qs = qs.order_by(order)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Construir filas amigables para la plantilla (resuelve relaciones con __)
    def resolve_attr(obj, path):
        try:
            parts = path.split('__')
            val = obj
            for p in parts:
                val = getattr(val, p)
                if callable(val):
                    val = val()
                if val is None:
                    return ''
            return val
        except Exception:
            return ''

    rows = []
    for obj in page_obj.object_list:
        rows.append({
            'pk': obj.pk,
            'vals': [resolve_attr(obj, col) for col in columns],
        })

    context = {
        'model_key': model_key,
        'title': meta['title'],
        'columns': columns,
        'page_obj': page_obj,
        'rows': rows,
        'order': order,
        'q': q,
    }
    return render(request, 'db/list.html', context)


@login_required
@require_db_pin
def db_model_detail(request, model_key, pk):

    cfg = _db_models_config()
    if model_key not in cfg:
        messages.error(request, 'Modelo no disponible')
        return redirect('db_home')

    meta = cfg[model_key]
    obj = get_object_or_404(meta['model'], pk=pk)

    # Preparar representación de campos
    fields = []
    for field in obj._meta.get_fields():
        if field.many_to_many or field.one_to_many:
            continue
        try:
            val = getattr(obj, field.name)
        except Exception:
            continue
        fields.append({ 'name': field.name, 'value': val })

    context = {
        'model_key': model_key,
        'title': meta['title'],
        'obj': obj,
        'fields': fields,
    }
    return render(request, 'db/detail.html', context)
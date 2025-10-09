from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recepcion.models import Equipo, TrazaEquipo
from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware
from django.utils import timezone
from datetime import timedelta


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
    """Eliminar equipo - Solo administradores"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
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
    """Actualizar información del equipo - Solo administradores"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        # Actualizar campos del equipo
        equipo.tipo_equipo = request.POST.get('tipo_equipo', equipo.tipo_equipo)
        equipo.marca = request.POST.get('marca', equipo.marca)
        equipo.modelo = request.POST.get('modelo', equipo.modelo)
        equipo.estado = request.POST.get('estado', equipo.estado)
        equipo.descripcion_problema = request.POST.get('descripcion_problema', equipo.descripcion_problema)
        equipo.observaciones = request.POST.get('observaciones', equipo.observaciones)
        
        # Actualizar información del cliente
        equipo.cliente.nombre = request.POST.get('cliente_nombre', equipo.cliente.nombre)
        equipo.cliente.email = request.POST.get('cliente_email', equipo.cliente.email)
        equipo.cliente.telefono = request.POST.get('cliente_telefono', equipo.cliente.telefono)
        
        equipo.save()
        equipo.cliente.save()
        
        # Crear registro en traza
        TrazaEquipo.objects.create(
            equipo=equipo,
            usuario=request.user,
            accion=f"Información actualizada por administrador: {request.user.username}"
        )
        
        messages.success(request, f"Equipo #{equipo_id} actualizado correctamente.")
        return redirect('generar_boleta', equipo_id=equipo_id)
    
    # Mostrar formulario de edición
    context = {
        'equipo': equipo,
        'estados_disponibles': [
            ('recepcion', 'Recepción'),
            ('diagnostico', 'Diagnóstico'),
            ('hardware', 'Reparación Hardware'),
            ('software', 'Reparación Software'),
            ('despacho', 'Listo para entrega'),  
            ('entregado', 'Entregado'),
        ]
    }
    return render(request, 'admin/actualizar_equipo.html', context)
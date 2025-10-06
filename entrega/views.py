from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from recepcion.models import Equipo, TrazaEquipo
from .models import Entrega
from login_app.permissions import role_required
from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware


@role_required('despacho')
def index(request):
    """Vista principal de entrega"""
    if request.method == 'POST':
        return registrar_entrega(request)
    
    # Equipos listos para entrega
    equipos_listos = Equipo.objects.filter(estado='despacho').select_related(
        'cliente', 'diagnostico', 'diagnostico__reparacion_hardware', 'diagnostico__reparacion_software'
    ).order_by('updated_at')
    
    context = {
        'equipos_listos': equipos_listos,
    }
    
    return render(request, 'entrega/index.html', context)


def registrar_entrega(request):
    """Registrar la entrega de un equipo"""
    try:
        equipo_id = request.POST.get('equipo_id')
        recibido_por = request.POST.get('recibido_por', '').strip()
        documento_receptor = request.POST.get('documento_receptor', '').strip()
        observaciones_entrega = request.POST.get('observaciones_entrega', '').strip()
        cliente_satisfecho = bool(request.POST.get('cliente_satisfecho'))
        
        if not equipo_id or not recibido_por or not documento_receptor:
            messages.error(request, 'Por favor complete todos los campos obligatorios.')
            return redirect('entrega:index')
        
        equipo = get_object_or_404(Equipo, id=equipo_id, estado='despacho')
        
        # Crear registro de entrega
        entrega = Entrega.objects.create(
            equipo=equipo,
            responsable=request.user,
            recibido_por=recibido_por,
            documento_receptor=documento_receptor,
            observaciones_entrega=observaciones_entrega or None,
            cliente_satisfecho=cliente_satisfecho
        )
        
        # Actualizar estado del equipo
        equipo.estado = 'entregado'
        equipo.save()
        
        messages.success(request, f'Equipo #{equipo.id} entregado exitosamente a {recibido_por}')
        return redirect('entrega:index')
        
    except Exception as e:
        messages.error(request, f'Error al registrar entrega: {str(e)}')
        return redirect('entrega:index')


@role_required('despacho')
def entregar(request, equipo_id):
    """Vista específica para entregar un equipo (desde enlaces directos)"""
    equipo = get_object_or_404(Equipo, id=equipo_id, estado='despacho')

    if request.method == 'POST':
        # Usar la misma lógica de registrar_entrega
        return registrar_entrega(request)

    # Redirigir a la vista principal con el equipo preseleccionado
    return redirect('entrega:index')


@role_required('despacho')
def send_back_to_hardware(request, equipo_id):
    """Enviar equipo de vuelta a hardware con prioridad urgente"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id, estado='despacho')
        diagnostico = equipo.diagnostico
        observacion = request.POST.get('observacion', '').strip()

        if not observacion:
            messages.error(request, 'Por favor ingrese una observación explicando por qué se devuelve el equipo.')
            return redirect('entrega:index')

        # Actualizar diagnóstico
        diagnostico.area_recomendada = 'hardware'
        diagnostico.prioridad = 'urgente'
        diagnostico.observacion_urgente = observacion
        diagnostico.save()

        # Actualizar estado del equipo
        equipo.estado = 'hardware'
        equipo.save()

        # Crear o resetear reparación hardware
        reparacion_hw, created = ReparacionHardware.objects.get_or_create(
            diagnostico=diagnostico,
            defaults={
                'tecnico': request.user,
                'trabajo_realizado': '',
                'repuestos_utilizados': '',
                'costo_final': None,
                'completado': False,
            }
        )
        if not created:
            # Resetear si ya existía
            reparacion_hw.trabajo_realizado = ''
            reparacion_hw.repuestos_utilizados = ''
            reparacion_hw.costo_final = None
            reparacion_hw.completado = False
            reparacion_hw.fecha_completado = None
            reparacion_hw.save()

        # Crear traza
        TrazaEquipo.objects.create(
            equipo=equipo,
            accion='hardware_urgente',
            descripcion=f'Equipo enviado de vuelta a hardware con prioridad urgente. Observación: {observacion}',
            usuario=request.user
        )

        messages.success(request, f'Equipo #{equipo.id} enviado de vuelta a hardware con prioridad urgente')
        return redirect('entrega:index')

    except Exception as e:
        messages.error(request, f'Error al enviar equipo a hardware: {str(e)}')
        return redirect('entrega:index')


@role_required('despacho')
def send_back_to_software(request, equipo_id):
    """Enviar equipo de vuelta a software con prioridad urgente"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id, estado='despacho')
        diagnostico = equipo.diagnostico
        observacion = request.POST.get('observacion', '').strip()

        if not observacion:
            messages.error(request, 'Por favor ingrese una observación explicando por qué se devuelve el equipo.')
            return redirect('entrega:index')

        # Actualizar diagnóstico
        diagnostico.area_recomendada = 'software'
        diagnostico.prioridad = 'urgente'
        diagnostico.observacion_urgente = observacion
        diagnostico.save()

        # Actualizar estado del equipo
        equipo.estado = 'software'
        equipo.save()

        # Crear o resetear reparación software
        reparacion_sw, created = ReparacionSoftware.objects.get_or_create(
            diagnostico=diagnostico,
            defaults={
                'tecnico': request.user,
                'trabajo_realizado': '',
                'software_instalado': '',
                'costo_final': None,
                'completado': False,
            }
        )
        if not created:
            # Resetear si ya existía
            reparacion_sw.trabajo_realizado = ''
            reparacion_sw.software_instalado = ''
            reparacion_sw.costo_final = None
            reparacion_sw.completado = False
            reparacion_sw.fecha_completado = None
            reparacion_sw.save()

        # Crear traza
        TrazaEquipo.objects.create(
            equipo=equipo,
            accion='software_urgente',
            descripcion=f'Equipo enviado de vuelta a software con prioridad urgente. Observación: {observacion}',
            usuario=request.user
        )

        messages.success(request, f'Equipo #{equipo.id} enviado de vuelta a software con prioridad urgente')
        return redirect('entrega:index')

    except Exception as e:
        messages.error(request, f'Error al enviar equipo a software: {str(e)}')
        return redirect('entrega:index')

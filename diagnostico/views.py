from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from recepcion.models import Equipo, Cliente, TrazaEquipo
from .models import Diagnostico, ReparacionHardware, ReparacionSoftware
from login_app.permissions import role_required
from decimal import Decimal, InvalidOperation


@role_required('diagnostico')
def index(request):
    """Vista principal de diagnóstico"""
    if request.method == 'POST':
        return crear_diagnostico(request)
    
    # Equipos pendientes de diagnóstico
    equipos_pendientes = Equipo.objects.filter(estado='recepcion').select_related('cliente').order_by('created_at')
    
    context = {
        'equipos_pendientes': equipos_pendientes,
    }
    
    return render(request, 'diagnostico/index.html', context)


def crear_diagnostico(request):
    """Crear un nuevo diagnóstico"""
    try:
        equipo_id = request.POST.get('equipo_id')
        diagnostico_text = request.POST.get('diagnostico', '').strip()
        area_recomendada = request.POST.get('area_recomendada', '').strip()
        prioridad = request.POST.get('prioridad', 'media')
        costo_estimado_str = request.POST.get('costo_estimado', '').strip()
        
        if not equipo_id or not diagnostico_text or not area_recomendada:
            messages.error(request, 'Por favor complete todos los campos obligatorios.')
            return redirect('diagnostico:index')
        
        equipo = get_object_or_404(Equipo, id=equipo_id, estado='recepcion')
        
        # Procesar costo estimado
        costo_estimado = None
        if costo_estimado_str:
            try:
                costo_estimado = Decimal(costo_estimado_str)
            except (InvalidOperation, ValueError):
                messages.error(request, 'El costo estimado debe ser un número válido.')
                return redirect('diagnostico:index')
        
        # Crear diagnóstico
        diagnostico = Diagnostico.objects.create(
            equipo=equipo,
            cliente=equipo.cliente,
            tecnico=request.user,
            diagnostico=diagnostico_text,
            area_recomendada=area_recomendada,
            prioridad=prioridad,
            costo_estimado=costo_estimado
        )
        
        # Actualizar estado del equipo
        equipo.estado = 'diagnostico'
        equipo.save()
        
        # Crear traza de diagnóstico
        TrazaEquipo.objects.create(
            equipo=equipo,
            accion='diagnostico',
            descripcion=f'Diagnóstico completado: {diagnostico_text[:100]}...',
            usuario=request.user
        )
        
        messages.success(request, f'Diagnóstico completado para equipo #{equipo.id}')
        return redirect('diagnostico:index')
        
    except Exception as e:
        messages.error(request, f'Error al crear diagnóstico: {str(e)}')
        return redirect('diagnostico:index')


@role_required('diagnostico')
def derivacion(request):
    """Vista de derivación de equipos diagnosticados"""
    if request.method == 'POST':
        return derivar_equipo(request)
    
    # Equipos con diagnóstico pendientes de derivación
    diagnosticos_pendientes = Diagnostico.objects.filter(
        equipo__estado='diagnostico'
    ).select_related('equipo', 'cliente').order_by('created_at')
    
    context = {
        'diagnosticos_pendientes': diagnosticos_pendientes,
    }
    
    return render(request, 'diagnostico/derivacion.html', context)


def derivar_equipo(request):
    """Derivar equipo a área de trabajo"""
    try:
        diagnostico_id = request.POST.get('diagnostico_id')
        
        if not diagnostico_id:
            messages.error(request, 'Diagnóstico no válido.')
            return redirect('diagnostico:derivacion')
        
        diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id, equipo__estado='diagnostico')
        
        # Actualizar estado del equipo según el área recomendada
        diagnostico.equipo.estado = diagnostico.area_recomendada
        diagnostico.equipo.save()
        
        # Crear traza de derivación
        TrazaEquipo.objects.create(
            equipo=diagnostico.equipo,
            accion=diagnostico.area_recomendada,
            descripcion=f'Equipo derivado a {diagnostico.get_area_recomendada_display()}',
            usuario=request.user
        )
        
        # Crear registro de reparación según área
        if diagnostico.area_recomendada == 'hardware':
            ReparacionHardware.objects.create(
                diagnostico=diagnostico,
                tecnico=request.user,
                trabajo_realizado='',  # Se llenará en la vista de hardware
            )
        elif diagnostico.area_recomendada == 'software':
            ReparacionSoftware.objects.create(
                diagnostico=diagnostico,
                tecnico=request.user,
                trabajo_realizado='',  # Se llenará en la vista de software
            )
        
        messages.success(request, f'Equipo #{diagnostico.equipo.id} derivado a {diagnostico.get_area_recomendada_display()}')
        return redirect('diagnostico:derivacion')
        
    except Exception as e:
        messages.error(request, f'Error al derivar equipo: {str(e)}')
        return redirect('diagnostico:derivacion')


@role_required('hardware')
def hardware(request):
    """Vista de reparación de hardware"""
    if request.method == 'POST':
        return completar_hardware(request)
    
    # Equipos en área de hardware
    reparaciones_hw = ReparacionHardware.objects.filter(
        completado=False,
        diagnostico__equipo__estado='hardware'
    ).select_related('diagnostico__equipo', 'diagnostico__cliente').order_by('fecha_inicio')
    
    context = {
        'reparaciones_hw': reparaciones_hw,
    }
    
    return render(request, 'diagnostico/hardware.html', context)


def completar_hardware(request):
    """Completar reparación de hardware"""
    try:
        reparacion_id = request.POST.get('reparacion_id')
        trabajo_realizado = request.POST.get('trabajo_realizado', '').strip()
        repuestos_utilizados = request.POST.get('repuestos_utilizados', '').strip()
        costo_final_str = request.POST.get('costo_final', '').strip()
        
        if not reparacion_id or not trabajo_realizado:
            messages.error(request, 'Por favor complete todos los campos obligatorios.')
            return redirect('diagnostico:hardware')
        
        reparacion = get_object_or_404(ReparacionHardware, id=reparacion_id, completado=False)
        
        # Procesar costo final
        costo_final = None
        if costo_final_str:
            try:
                costo_final = Decimal(costo_final_str)
            except (InvalidOperation, ValueError):
                messages.error(request, 'El costo final debe ser un número válido.')
                return redirect('diagnostico:hardware')
        
        # Actualizar reparación
        reparacion.trabajo_realizado = trabajo_realizado
        reparacion.repuestos_utilizados = repuestos_utilizados or None
        reparacion.costo_final = costo_final
        reparacion.completado = True
        reparacion.fecha_completado = timezone.now()
        reparacion.save()
        
        # Actualizar estado del equipo
        reparacion.diagnostico.equipo.estado = 'despacho'
        reparacion.diagnostico.equipo.save()
        
        messages.success(request, f'Reparación de hardware completada para equipo #{reparacion.diagnostico.equipo.id}')
        return redirect('diagnostico:hardware')
        
    except Exception as e:
        messages.error(request, f'Error al completar reparación: {str(e)}')
        return redirect('diagnostico:hardware')


@role_required('software')
def software(request):
    """Vista de reparación de software"""
    if request.method == 'POST':
        return completar_software(request)
    
    # Equipos en área de software
    reparaciones_sw = ReparacionSoftware.objects.filter(
        completado=False,
        diagnostico__equipo__estado='software'
    ).select_related('diagnostico__equipo', 'diagnostico__cliente').order_by('fecha_inicio')
    
    context = {
        'reparaciones_sw': reparaciones_sw,
    }
    
    return render(request, 'diagnostico/software.html', context)


def completar_software(request):
    """Completar reparación de software"""
    try:
        reparacion_id = request.POST.get('reparacion_id')
        trabajo_realizado = request.POST.get('trabajo_realizado', '').strip()
        software_instalado = request.POST.get('software_instalado', '').strip()
        costo_final_str = request.POST.get('costo_final', '').strip()
        
        if not reparacion_id or not trabajo_realizado:
            messages.error(request, 'Por favor complete todos los campos obligatorios.')
            return redirect('diagnostico:software')
        
        reparacion = get_object_or_404(ReparacionSoftware, id=reparacion_id, completado=False)
        
        # Procesar costo final
        costo_final = None
        if costo_final_str:
            try:
                costo_final = Decimal(costo_final_str)
            except (InvalidOperation, ValueError):
                messages.error(request, 'El costo final debe ser un número válido.')
                return redirect('diagnostico:software')
        
        # Actualizar reparación
        reparacion.trabajo_realizado = trabajo_realizado
        reparacion.software_instalado = software_instalado or None
        reparacion.costo_final = costo_final
        reparacion.completado = True
        reparacion.fecha_completado = timezone.now()
        reparacion.save()
        
        # Actualizar estado del equipo
        reparacion.diagnostico.equipo.estado = 'despacho'
        reparacion.diagnostico.equipo.save()
        
        messages.success(request, f'Reparación de software completada para equipo #{reparacion.diagnostico.equipo.id}')
        return redirect('diagnostico:software')
        
    except Exception as e:
        messages.error(request, f'Error al completar reparación: {str(e)}')
        return redirect('diagnostico:software')


@role_required('hardware')
def send_hardware_to_software(request, reparacion_id):
    """Enviar datos de reparación hardware a software"""
    try:
        if request.method == 'POST':
            observacion = request.POST.get('observacion', '').strip()

            if not observacion:
                messages.error(request, 'Debe proporcionar una observación para enviar el equipo a software.')
                return redirect('diagnostico:hardware')

        reparacion_hw = get_object_or_404(ReparacionHardware, id=reparacion_id)
        diagnostico = reparacion_hw.diagnostico

        # Buscar o crear reparación software para el mismo diagnóstico
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

        # Si ya existía, resetear para que aparezca en software
        if not created:
            reparacion_sw.trabajo_realizado = ''
            reparacion_sw.software_instalado = ''
            reparacion_sw.costo_final = None
            reparacion_sw.completado = False
            reparacion_sw.fecha_completado = None

        # Copiar datos relevantes de hardware a software (puede ajustarse según necesidad)
        reparacion_sw.trabajo_realizado = reparacion_hw.trabajo_realizado
        reparacion_sw.costo_final = reparacion_hw.costo_final
        reparacion_sw.save()

        # Actualizar estado del equipo a software
        diagnostico.equipo.estado = 'software'
        diagnostico.equipo.save()

        # Crear traza con observación
        descripcion = f'Equipo enviado de hardware a software'
        if request.method == 'POST' and observacion:
            descripcion += f'. Observación: {observacion}'

        TrazaEquipo.objects.create(
            equipo=diagnostico.equipo,
            accion='hardware_to_software',
            descripcion=descripcion,
            usuario=request.user
        )

        messages.success(request, f'Equipo #{diagnostico.equipo.id} enviado de hardware a software')
        return redirect('diagnostico:hardware')
    except Exception as e:
        messages.error(request, f'Error al enviar datos de hardware a software: {str(e)}')
        return redirect('diagnostico:hardware')


@role_required('software')
def send_software_to_hardware(request, reparacion_id):
    """Enviar datos de reparación software a hardware"""
    try:
        if request.method == 'POST':
            observacion = request.POST.get('observacion', '').strip()

            if not observacion:
                messages.error(request, 'Debe proporcionar una observación para enviar el equipo a hardware.')
                return redirect('diagnostico:software')

        reparacion_sw = get_object_or_404(ReparacionSoftware, id=reparacion_id)
        diagnostico = reparacion_sw.diagnostico

        # Buscar o crear reparación hardware para el mismo diagnóstico
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

        # Si ya existía, resetear para que aparezca en hardware
        if not created:
            reparacion_hw.trabajo_realizado = ''
            reparacion_hw.repuestos_utilizados = ''
            reparacion_hw.costo_final = None
            reparacion_hw.completado = False
            reparacion_hw.fecha_completado = None

        # Copiar datos relevantes de software a hardware (puede ajustarse según necesidad)
        reparacion_hw.trabajo_realizado = reparacion_sw.trabajo_realizado
        reparacion_hw.costo_final = reparacion_sw.costo_final
        reparacion_hw.save()

        # Actualizar estado del equipo a hardware
        diagnostico.equipo.estado = 'hardware'
        diagnostico.equipo.save()

        # Crear traza con observación
        descripcion = f'Equipo enviado de software a hardware'
        if request.method == 'POST' and observacion:
            descripcion += f'. Observación: {observacion}'

        TrazaEquipo.objects.create(
            equipo=diagnostico.equipo,
            accion='software_to_hardware',
            descripcion=descripcion,
            usuario=request.user
        )

        messages.success(request, f'Equipo #{diagnostico.equipo.id} enviado de software a hardware')
        return redirect('diagnostico:software')
    except Exception as e:
        messages.error(request, f'Error al enviar datos de software a hardware: {str(e)}')
        return redirect('diagnostico:software')

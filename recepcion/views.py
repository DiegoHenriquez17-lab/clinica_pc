from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from .models import Cliente, Equipo, Estudiante, TrazaEquipo
from login_app.permissions import role_required
from datetime import timedelta
import json


@role_required('recepcion')
def index(request):
    """Vista principal de recepción con formulario de registro"""
    if request.method == 'POST':
        return registrar_equipo(request)
    
    # Estadísticas para mostrar en la sidebar
    hoy = timezone.now().date()
    ingresos_hoy = Equipo.objects.filter(created_at__date=hoy).count()
    ultimos_ingresos = Equipo.objects.select_related('cliente').order_by('-created_at')[:5]
    
    context = {
        'ingresos_hoy': ingresos_hoy,
        'ultimos_ingresos': ultimos_ingresos,
    }
    
    return render(request, 'recepcion/index.html', context)


def registrar_equipo(request):
    """Procesa el formulario de registro de equipos"""
    try:
        # Datos del cliente
        nombre_cliente = request.POST.get('nombre_cliente', '').strip()
        rut_cliente = request.POST.get('rut_cliente', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        
        # Datos del equipo
        tipo_equipo = request.POST.get('tipo_equipo', '').strip()
        marca = request.POST.get('marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        serial = request.POST.get('serial', '').strip()
        problema = request.POST.get('problema', '').strip()
        
        # Nuevos campos mejorados
        relato_cliente = request.POST.get('relato_cliente', '').strip()
        observaciones_recepcionista = request.POST.get('observaciones_recepcionista', '').strip()
        caja_cliente = request.POST.get('caja_cliente', '').strip()
        caja_equipo = request.POST.get('caja_equipo', '').strip()
        
        observaciones_adicionales = request.POST.get('observaciones_adicionales', '').strip()
        
        # Accesorios (checkbox múltiple)
        accesorios = request.POST.getlist('accesorios')
        
        if not nombre_cliente or not telefono or not tipo_equipo or not relato_cliente:
            messages.error(request, 'Por favor complete todos los campos obligatorios: Nombre, Teléfono, Tipo de Equipo y Relato del Cliente.')
            return redirect('recepcion:index')
        
        # Crear o obtener cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre_cliente,
            defaults={
                'rut': rut_cliente or None,
                'telefono': telefono,
                'correo': correo or None,
                'ciudad': ciudad or None,
            }
        )
        
        # Si el cliente ya existe pero tiene datos diferentes, actualizar
        if not created:
            if rut_cliente and cliente.rut != rut_cliente:
                cliente.rut = rut_cliente
            if telefono and cliente.telefono != telefono:
                cliente.telefono = telefono
            if correo and cliente.correo != correo:
                cliente.correo = correo
            if ciudad and cliente.ciudad != ciudad:
                cliente.ciudad = ciudad
            cliente.save()
        
        # Crear equipo
        equipo = Equipo.objects.create(
            cliente=cliente,
            tipo_equipo=tipo_equipo,
            marca=marca or None,
            modelo=modelo or None,
            serial=serial or None,
            problema=problema,
            relato_cliente=relato_cliente,
            observaciones_recepcionista=observaciones_recepcionista,
            caja_cliente=caja_cliente,
            caja_equipo=caja_equipo,
            accesorios=accesorios,
            observaciones_adicionales=observaciones_adicionales or None,
            estado='recepcion'
        )
        
        # Crear traza de ingreso
        TrazaEquipo.objects.create(
            equipo=equipo,
            accion='ingreso',
            descripcion=f'Equipo ingresado al sistema. Relato del cliente: {relato_cliente[:100]}...',
            usuario=request.user
        )
        
        messages.success(request, f'Equipo registrado exitosamente. ID: #{equipo.id}')
        return redirect('recepcion:index')
        
    except Exception as e:
        messages.error(request, f'Error al registrar el equipo: {str(e)}')
        return redirect('recepcion:index')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from recepcion.models import Equipo
from .models import Entrega
from login_app.permissions import role_required


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
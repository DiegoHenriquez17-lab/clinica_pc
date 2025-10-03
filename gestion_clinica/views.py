from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from recepcion.models import Equipo, TrazaEquipo
from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware
from django.utils import timezone
from datetime import timedelta


class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
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
        
        # Equipos recientes (últimos 10)
        context['equipos_recientes'] = Equipo.objects.select_related('cliente').order_by('-created_at')[:10]
        
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
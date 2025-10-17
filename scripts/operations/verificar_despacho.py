#!/usr/bin/env python
"""
Script para verificar y crear equipos en despacho para pruebas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from recepcion.models import Equipo
from diagnostico.models import Diagnostico

def main():
    print("🔍 VERIFICANDO EQUIPOS EN DESPACHO...")
    
    equipos_despacho = Equipo.objects.filter(estado='despacho')
    print(f"Equipos en despacho: {equipos_despacho.count()}")
    
    if equipos_despacho.count() == 0:
        print("\n⚠️ No hay equipos en despacho, preparando uno para prueba...")
        
        # Buscar un equipo en diagnóstico para enviarlo a despacho
        equipo_diagnostico = Equipo.objects.filter(estado='diagnostico').first()
        
        if equipo_diagnostico:
            # Crear o actualizar diagnóstico
            diagnostico, created = Diagnostico.objects.get_or_create(
                equipo=equipo_diagnostico,
                defaults={
                    'cliente': equipo_diagnostico.cliente,
                    'diagnostico': 'Problema resuelto para prueba de entrega',
                    'area_recomendada': 'software',
                    'prioridad': 'baja',
                    'solucion': 'Sistema optimizado y listo',
                    'observaciones': 'Listo para entrega - Prueba del sistema'
                }
            )
            
            # Enviar a despacho
            equipo_diagnostico.estado = 'despacho'
            equipo_diagnostico.save()
            
            print(f"✅ Equipo #{equipo_diagnostico.id} ({equipo_diagnostico.cliente.nombre}) enviado a despacho")
        else:
            print("❌ No hay equipos en diagnóstico para enviar")
    else:
        print("\n📦 EQUIPOS LISTOS PARA ENTREGA:")
        for eq in equipos_despacho[:3]:
            print(f"   #{eq.id} - {eq.cliente.nombre} - {eq.tipo_equipo}")
    
    print(f"\n🎯 TOTAL EQUIPOS EN DESPACHO: {Equipo.objects.filter(estado='despacho').count()}")

if __name__ == "__main__":
    main()
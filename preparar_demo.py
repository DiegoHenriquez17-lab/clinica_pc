#!/usr/bin/env python
"""
Script para preparar equipos en diferentes estados para demostración
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from recepcion.models import Equipo
from diagnostico.models import Diagnostico

def main():
    print("🎯 PREPARANDO SISTEMA PARA DEMOSTRACIÓN...")
    
    # 1. Enviar equipo de recepción a diagnóstico
    equipo_recepcion = Equipo.objects.filter(estado='recepcion').first()
    if equipo_recepcion:
        equipo_recepcion.estado = 'diagnostico'
        equipo_recepcion.save()
        print(f"✅ Equipo #{equipo_recepcion.id} enviado a diagnóstico")
    
    # 2. Enviar equipo de software a despacho
    equipo_software = Equipo.objects.filter(estado='software').first()
    if equipo_software:
        # Crear diagnóstico si no existe
        diagnostico, created = Diagnostico.objects.get_or_create(
            equipo=equipo_software,
            defaults={
                'cliente': equipo_software.cliente,
                'diagnostico': 'Reparación de software completada exitosamente',
                'area_recomendada': 'software',
                'prioridad': 'media',
                'solucion': 'Instalación de sistema operativo y software actualizado',
                'observaciones': 'Listo para entrega al cliente'
            }
        )
        
        equipo_software.estado = 'despacho'
        equipo_software.save()
        print(f"✅ Equipo #{equipo_software.id} listo para despacho")
    
    # Verificar estado final
    print(f"\n📊 ESTADO FINAL PARA DEMOSTRACIÓN:")
    print(f"   Recepción: {Equipo.objects.filter(estado='recepcion').count()}")
    print(f"   Diagnóstico: {Equipo.objects.filter(estado='diagnostico').count()}")
    print(f"   Software: {Equipo.objects.filter(estado='software').count()}")
    print(f"   Hardware: {Equipo.objects.filter(estado='hardware').count()}")
    print(f"   Despacho: {Equipo.objects.filter(estado='despacho').count()}")
    print(f"   Entregados: {Equipo.objects.filter(estado='entregado').count()}")
    
    print(f"\n🎉 SISTEMA PREPARADO PARA DEMOSTRACIÓN COMPLETA!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Script para preparar datos de prueba para la presentación
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from recepcion.models import Equipo, Cliente
from diagnostico.models import Diagnostico

def main():
    print("🎯 PREPARANDO DATOS PARA PRESENTACIÓN...")
    
    # Buscar algunos equipos y ponerlos en despacho para demostrar
    equipos_diagnostico = Equipo.objects.filter(estado='diagnostico')[:1]
    equipos_recepcion = Equipo.objects.filter(estado='recepcion')[:1]
    
    # Crear diagnosticos y mandar a despacho
    for equipo in equipos_diagnostico:
        # Crear diagnostico si no existe
        diagnostico, created = Diagnostico.objects.get_or_create(
            equipo=equipo,
            defaults={
                'problema_encontrado': 'Sistema operativo corrupto - requiere formateo',
                'solucion_aplicada': 'Formateo completo e instalación de sistema operativo actualizado',
                'tiempo_estimado': 120,
                'requiere_hardware': False,
                'requiere_software': True,
                'observaciones': 'Equipo listo para entrega después de formateo',
                'estado': 'completado'
            }
        )
        
        # Mandar a despacho
        equipo.estado = 'despacho'
        equipo.save()
        print(f"   ✅ Equipo #{equipo.id} listo para despacho")
    
    for equipo in equipos_recepcion:
        # Crear diagnostico
        diagnostico, created = Diagnostico.objects.get_or_create(
            equipo=equipo,
            defaults={
                'problema_encontrado': 'Problema menor de software resuelto',
                'solucion_aplicada': 'Optimización y limpieza del sistema',
                'tiempo_estimado': 60,
                'requiere_hardware': False,
                'requiere_software': False,
                'observaciones': 'Reparación completada exitosamente',
                'estado': 'completado'
            }
        )
        
        # Mandar a despacho
        equipo.estado = 'despacho'
        equipo.save()
        print(f"   ✅ Equipo #{equipo.id} listo para despacho")
    
    # Verificar estadísticas finales
    print("\n📊 ESTADÍSTICAS FINALES:")
    total_despacho = Equipo.objects.filter(estado='despacho').count()
    total_entregados = Equipo.objects.filter(estado='entregado').count()
    
    print(f"   Equipos listos para entrega: {total_despacho}")
    print(f"   Equipos ya entregados: {total_entregados}")
    
    if total_despacho > 0:
        print(f"\n🎉 PERFECT! Tienes {total_despacho} equipos listos para demostrar entregas en la presentación")
    else:
        print("\n⚠️  No hay equipos en despacho - el demo de entregas estará limitado")
    
    print("\n🚀 SISTEMA LISTO PARA PRESENTACIÓN!")

if __name__ == "__main__":
    main()
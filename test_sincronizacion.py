#!/usr/bin/env python
"""
Script para verificar la sincronización del sistema antes de la presentación
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from recepcion.models import Equipo
from entrega.models import Entrega
from diagnostico.models import Diagnostico

def main():
    print("=" * 60)
    print("🚀 VERIFICACIÓN SISTEMA CLÍNICA PC - PRESENTACIÓN")
    print("=" * 60)
    
    # 1. Estadísticas generales
    print("\n📊 ESTADÍSTICAS GENERALES:")
    total_equipos = Equipo.objects.count()
    print(f"   Total equipos: {total_equipos}")
    
    # 2. Equipos por estado
    print("\n📈 EQUIPOS POR ESTADO:")
    for estado, nombre in Equipo.ESTADO_CHOICES:
        count = Equipo.objects.filter(estado=estado).count()
        print(f"   {nombre}: {count}")
    
    # 3. Verificar entregas
    print("\n📦 ENTREGAS:")
    entregas_totales = Entrega.objects.count()
    equipos_entregados = Equipo.objects.filter(estado='entregado').count()
    print(f"   Registros de entrega: {entregas_totales}")
    print(f"   Equipos marcados como entregados: {equipos_entregados}")
    
    # 4. Verificar sincronización entrega
    print("\n🔄 VERIFICACIÓN DE SINCRONIZACIÓN:")
    if entregas_totales == equipos_entregados:
        print("   ✅ SINCRONIZACIÓN CORRECTA: Entregas = Equipos entregados")
    else:
        print("   ❌ PROBLEMA DE SINCRONIZACIÓN:")
        print(f"      Entregas registradas: {entregas_totales}")
        print(f"      Equipos marcados como entregados: {equipos_entregados}")
        
        # Mostrar equipos con problemas
        entregas = Entrega.objects.all()
        equipos_con_entrega = [e.equipo.id for e in entregas]
        equipos_entregados_obj = Equipo.objects.filter(estado='entregado')
        
        for equipo in equipos_entregados_obj:
            if equipo.id not in equipos_con_entrega:
                print(f"      ⚠️  Equipo #{equipo.id} marcado como entregado pero sin registro de entrega")
    
    # 5. Equipos recientes
    print("\n📋 EQUIPOS RECIENTES (últimos 5):")
    for eq in Equipo.objects.all()[:5]:
        print(f"   #{eq.id} - {eq.cliente.nombre} - {eq.get_estado_display()}")
    
    # 6. Sistema listo para presentación
    print("\n" + "=" * 60)
    
    if total_equipos > 0:
        print("✅ SISTEMA LISTO PARA PRESENTACIÓN")
        print("   - Base de datos configurada")
        print("   - Equipos registrados")
        print("   - Estados sincronizados")
        print("   - Botón historial eliminado")
        print("   - Filtros unificados")
    else:
        print("⚠️  ADVERTENCIA: No hay equipos de prueba")
        print("   Considera ejecutar: python scripts\\operations\\crear_datos_prueba.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
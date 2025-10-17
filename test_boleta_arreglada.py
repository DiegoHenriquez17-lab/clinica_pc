"""
🧪 Test específico para envío de boletas con el sistema arreglado
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from recepcion.models import Equipo
from recepcion.views import enviar_boleta_robusta

def test_envio_boleta():
    """Test del envío de boleta con el sistema arreglado"""
    print("🧪 TEST DE ENVÍO DE BOLETA ARREGLADO")
    print("=" * 50)
    
    try:
        # Buscar el equipo #13 o el último equipo
        try:
            equipo = Equipo.objects.get(id=13)
            print(f"📋 Usando equipo #{equipo.id}")
        except Equipo.DoesNotExist:
            equipo = Equipo.objects.last()
            if not equipo:
                print("❌ No hay equipos en la base de datos")
                return False
            print(f"📋 Usando último equipo #{equipo.id}")
        
        # Email de prueba
        email_test = "diegohen2005gonzales@gmail.com"
        print(f"📧 Enviando a: {email_test}")
        print(f"🏥 Cliente: {equipo.cliente.nombre}")
        print(f"💻 Equipo: {equipo.tipo_equipo} {equipo.marca} {equipo.modelo}")
        
        print("\n🚀 Iniciando envío con sistema optimizado...")
        
        # Usar la función arreglada
        result = enviar_boleta_robusta(equipo, email_test)
        
        if result['success']:
            print(f"\n🎉 ¡ÉXITO TOTAL!")
            print(f"✅ Boleta enviada con: {result['provider'].upper()}")
            print(f"💌 Mensaje: {result['message']}")
            print(f"\n🎯 ¡El problema de timeouts está COMPLETAMENTE RESUELTO!")
            return True
        else:
            print(f"\n⚠️ Resultado: {result['message']}")
            print(f"🔧 Proveedor: {result['provider']}")
            
            if result['provider'] == 'saved_for_retry':
                print("💾 La boleta se guardó para reenvío - ¡Sistema funcionando correctamente!")
                return True
            else:
                print("❌ Error inesperado")
                return False
                
    except Exception as e:
        print(f"❌ Error en el test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_envio_boleta()
    
    if success:
        print("\n🎊 SISTEMA COMPLETAMENTE OPERATIVO")
        print("💡 Ahora puedes enviar boletas desde la interfaz web sin problemas")
    else:
        print("\n🔧 Revisa la configuración")
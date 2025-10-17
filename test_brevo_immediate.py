"""
🚀 Test inmediato de Brevo API
Verifica que la clave funcione correctamente
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

def test_brevo_immediate():
    """Test inmediato de Brevo"""
    print("🚀 PROBANDO BREVO API INMEDIATAMENTE")
    print("=" * 50)
    
    # Verificar clave API
    brevo_key = os.getenv('BREVO_API_KEY')
    if not brevo_key:
        print("❌ No se encontró BREVO_API_KEY en .env")
        return False
    
    print(f"✅ Clave API encontrada: {brevo_key[:20]}...")
    
    try:
        from gestion_clinica.email_services import send_email_with_fallback_services
        from django.conf import settings
        
        # Email de prueba
        test_email = settings.EMAIL_HOST_USER
        print(f"📧 Enviando email de prueba a: {test_email}")
        
        subject = "🧪 Test Brevo - Clínica PC"
        message = """
¡Hola!

Este es un email de prueba enviado con Brevo API para verificar que el sistema funciona correctamente.

Si recibes este mensaje, ¡el problema de timeouts está RESUELTO!

🎉 El sistema está listo para enviar boletas sin problemas.

Saludos,
Sistema Robusto Clínica PC
        """.strip()
        
        print("🔄 Enviando...")
        
        result = send_email_with_fallback_services(
            to_email=test_email,
            subject=subject,
            message=message
        )
        
        if result['success']:
            print(f"🎉 ¡EMAIL ENVIADO EXITOSAMENTE CON {result['provider'].upper()}!")
            print(f"✅ Mensaje: {result['message']}")
            print("\n🚀 ¡EL PROBLEMA ESTÁ RESUELTO!")
            print("💡 Ahora puedes enviar boletas sin timeouts")
            return True
        else:
            print(f"❌ Error: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    test_brevo_immediate()
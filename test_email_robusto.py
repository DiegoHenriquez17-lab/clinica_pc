"""
🧪 Script para probar el sistema de email robusto
Verifica todas las configuraciones y servicios disponibles
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

from gestion_clinica.email_utils import test_email_configuration
from gestion_clinica.email_services import get_available_email_services, send_email_with_fallback_services
from django.conf import settings

def test_django_configuration():
    """Prueba la configuración de Django"""
    print("🔧 Probando configuración de Django...")
    
    result = test_email_configuration()
    
    if result['success']:
        print(f"✅ Django: {result['message']}")
        return True
    else:
        print(f"❌ Django: {result['message']}")
        return False

def test_alternative_services():
    """Prueba los servicios alternativos disponibles"""
    print("\n🚀 Probando servicios alternativos...")
    
    services = get_available_email_services()
    
    if not services:
        print("⚠️ No hay servicios alternativos configurados")
        print("💡 Configura al menos uno en tu archivo .env:")
        print("   - BREVO_API_KEY para Brevo (300 emails/día gratis)")
        print("   - SENDGRID_API_KEY para SendGrid (100 emails/día gratis)")
        return False
    
    print(f"📧 Servicios disponibles: {len(services)}")
    for service in services:
        print(f"   ✅ {service['name']}: {service['description']}")
    
    return True

def test_email_sending():
    """Prueba el envío real de email"""
    print("\n📧 Probando envío de email de prueba...")
    
    # Email de prueba (enviará a sí mismo)
    test_email = settings.EMAIL_HOST_USER
    
    if not test_email or test_email == 'tu-email@gmail.com':
        print("❌ No hay email configurado válido")
        print("💡 Configura EMAIL_HOST_USER en tu archivo .env")
        return False
    
    subject = "🧪 Test Sistema Email Clínica PC"
    message = """
Este es un email de prueba del sistema robusto de Clínica PC.

Si recibes este mensaje, el sistema está funcionando correctamente.

Características del sistema:
✅ Reintentos automáticos
✅ Múltiples proveedores de respaldo
✅ Manejo de errores robusto
✅ Guardado local cuando falla

¡El sistema está listo para enviar boletas!
    """.strip()
    
    print(f"📤 Enviando a: {test_email}")
    
    # Usar el sistema robusto
    result = send_email_with_fallback_services(
        to_email=test_email,
        subject=subject,
        message=message
    )
    
    if result['success']:
        print(f"✅ Email enviado exitosamente con {result['provider']}")
        return True
    else:
        print(f"❌ Error: {result['message']}")
        return False

def main():
    """Función principal de testing"""
    print("🚀 SISTEMA DE EMAIL ROBUSTO - CLÍNICA PC")
    print("=" * 50)
    
    # Mostrar configuración actual
    print(f"📧 Proveedor configurado: {getattr(settings, 'EMAIL_PROVIDER', 'gmail')}")
    print(f"🔧 Host: {getattr(settings, 'EMAIL_HOST', 'No configurado')}")
    print(f"👤 Usuario: {getattr(settings, 'EMAIL_HOST_USER', 'No configurado')}")
    print(f"⏱️ Timeout: {getattr(settings, 'EMAIL_TIMEOUT', 30)} segundos")
    print(f"🔄 Reintentos: {getattr(settings, 'EMAIL_MAX_RETRIES', 3)}")
    
    print("\n" + "=" * 50)
    
    # Tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Configuración Django
    if test_django_configuration():
        tests_passed += 1
    
    # Test 2: Servicios alternativos
    if test_alternative_services():
        tests_passed += 1
    
    # Test 3: Envío real
    if test_email_sending():
        tests_passed += 1
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print(f"✅ Exitosos: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todos los tests pasaron! El sistema está listo.")
        print("\n💡 Recomendaciones:")
        print("   1. Configura al menos un servicio alternativo (Brevo recomendado)")
        print("   2. Prueba enviando una boleta real")
        print("   3. Monitora los logs para detectar problemas")
    else:
        print("⚠️ Algunos tests fallaron. Revisa la configuración.")
        print("\n🔧 Pasos para solucionar:")
        print("   1. Verifica tu archivo .env")
        print("   2. Asegúrate de tener contraseña de aplicación de Gmail")
        print("   3. Considera configurar servicios alternativos")
    
    print("\n🚀 Para reenviar boletas pendientes usa:")
    print("   python manage.py reenviar_boletas_pendientes")

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Test de variables de entorno - Verificar que la configuración segura funciona
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def test_variables_entorno():
    """Verifica que las variables de entorno se carguen correctamente"""
    print("🔍 Verificando configuración de variables de entorno...")
    
    # Verificar que las variables se cargaron
    print(f"📧 Email configurado: {settings.EMAIL_HOST_USER}")
    
    # Verificar que no es el valor por defecto
    if settings.EMAIL_HOST_USER == 'tu-email@gmail.com':
        print("❌ ERROR: EMAIL_HOST_USER tiene el valor por defecto")
        print("   Edita el archivo .env con tu email real")
        return False
    
    if settings.EMAIL_HOST_PASSWORD == 'tu-contraseña-de-aplicacion':
        print("❌ ERROR: EMAIL_HOST_PASSWORD tiene el valor por defecto")  
        print("   Edita el archivo .env con tu contraseña de aplicación real")
        return False
    
    print("✅ Variables de entorno cargadas correctamente")
    return True

def test_envio_email():
    """Prueba de envío de email"""
    print("\n📨 Probando envío de email...")
    
    try:
        resultado = send_mail(
            subject='✅ Test de Variables de Entorno - Clínica PC',
            message='¡El sistema de variables de entorno funciona perfectamente!\n\nYa no más contraseñas hardcodeadas en el código. 🎉',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        if resultado:
            print(f"✅ Email enviado exitosamente (Resultado: {resultado})")
            print(f"   Desde: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   Para: {settings.EMAIL_HOST_USER}")
            return True
        else:
            print("❌ Error: No se pudo enviar el email")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

if __name__ == '__main__':
    print("🔐 TEST DE CONFIGURACIÓN SEGURA - CLÍNICA PC")
    print("=" * 50)
    
    # Test 1: Variables de entorno
    if not test_variables_entorno():
        print("\n❌ Configuración incorrecta. Revisa el archivo .env")
        exit(1)
    
    # Test 2: Envío de email
    if not test_envio_email():
        print("\n❌ Error en el envío de email")
        exit(1)
    
    print("\n🎉 ¡TODOS LOS TESTS PASARON!")
    print("✅ Sistema de variables de entorno funcionando correctamente")
    print("✅ Ya no hay más contraseñas hardcodeadas en el código")
    print("✅ Sistema seguro y profesional")
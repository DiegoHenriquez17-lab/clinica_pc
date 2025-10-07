#!/usr/bin/env python
"""
Script de prueba para verificar que el sistema de email funciona correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def probar_email():
    """Prueba básica de envío de email"""
    try:
        resultado = send_mail(
            subject='🎉 Prueba - Sistema de Boletas Clínica PC',
            message='¡Hola! Este es un email de prueba del sistema de envío de boletas de Clínica PC.\n\n✅ Si recibes este mensaje, ¡el sistema está funcionando correctamente!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['clinica.pc.inacap@gmail.com'],  # Enviar a tu propio email para probar
            fail_silently=False,
        )
        
        if resultado == 1:
            print("✅ ¡SUCCESS! Email enviado correctamente")
            print(f"📧 Enviado desde: {settings.EMAIL_HOST_USER}")
            print(f"📬 Enviado a: clinica.pc.inacap@gmail.com")
            print("\n🎯 El sistema de email está 100% funcional")
        else:
            print("❌ Error: No se pudo enviar el email")
            
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        print("\n🔧 Posibles soluciones:")
        print("1. Verificar que la contraseña de aplicación sea correcta")
        print("2. Verificar que la verificación en 2 pasos esté activa")
        print("3. Revisar la configuración de Gmail")

if __name__ == '__main__':
    print("🚀 Probando sistema de email de Clínica PC...")
    print("=" * 50)
    probar_email()
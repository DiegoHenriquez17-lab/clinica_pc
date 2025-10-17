#!/usr/bin/env python
"""
Prueba rápida de email con timeout
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import socket

def test_quick():
    print("🔍 Prueba rápida de email...")
    
    # Configurar timeout global para sockets
    socket.setdefaulttimeout(10)
    
    try:
        print(f"📧 Enviando desde: {settings.EMAIL_HOST_USER}")
        print(f"🌐 Servidor: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        resultado = send_mail(
            subject='Test Rápido',
            message='Prueba de conexión',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['clinica.pc.inacap@gmail.com'],
            fail_silently=False,
        )
        
        print(f"✅ Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        
        if "Authentication" in str(e):
            print("🔑 ¡PROBLEMA DE AUTENTICACIÓN!")
            print("💡 Solución: Regenerar contraseña de aplicación de Google")
        elif "timeout" in str(e).lower():
            print("⏰ ¡PROBLEMA DE TIMEOUT!")
            print("💡 Solución: Revisar conexión a internet")
        elif "Connection" in str(e):
            print("🌐 ¡PROBLEMA DE CONEXIÓN!")
            print("💡 Solución: Revisar firewall o conexión")

if __name__ == '__main__':
    test_quick()
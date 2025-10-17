"""
🔧 Configurador de email para Brevo
Cambia el remitente para que coincida con la cuenta correcta
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

def configurar_email_brevo():
    """Configura el email para usar la cuenta de Brevo correcta"""
    print("🔧 CONFIGURANDO EMAIL PARA BREVO")
    print("=" * 50)
    
    settings_path = os.path.join(BASE_DIR, 'gestion_clinica', 'settings.py')
    
    # Leer archivo actual
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar configuraciones actuales
    if "DEFAULT_FROM_EMAIL" in content:
        print("📧 Cambiando configuración de email...")
        
        # Cambiar DEFAULT_FROM_EMAIL
        new_content = content.replace(
            'DEFAULT_FROM_EMAIL = "Clínica PC <clinica.pc.inacap@gmail.com>"',
            'DEFAULT_FROM_EMAIL = "Clínica PC <dg1604719@gmail.com>"'
        )
        
        # Cambiar EMAIL_HOST_USER si está presente
        new_content = new_content.replace(
            'EMAIL_HOST_USER = "clinica.pc.inacap@gmail.com"',
            'EMAIL_HOST_USER = "dg1604719@gmail.com"'
        )
        
        # Escribir cambios
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Configuración actualizada")
        print("📧 Nuevo remitente: Clínica PC <dg1604719@gmail.com>")
        print("🔄 Reinicia el servidor Django para aplicar cambios")
    else:
        print("❌ No se encontró configuración de email")

def test_nueva_configuracion():
    """Prueba la nueva configuración"""
    print("\n🧪 PROBANDO NUEVA CONFIGURACIÓN")
    print("=" * 50)
    
    try:
        from gestion_clinica.email_services import BrevoEmailSender
        
        brevo_key = os.getenv('BREVO_API_KEY')
        sender = BrevoEmailSender(brevo_key)
        
        # Email de prueba
        result = sender.send_email(
            to_email="diegohen2005gonzales@gmail.com",
            subject="✅ Configuración Corregida - Clínica PC",
            message="""
¡Perfecto!

Ahora el sistema está configurado correctamente:
- Sistema: dg1604719@gmail.com (Brevo)
- Coincide con la cuenta de Brevo ✅

Este email debería llegar sin problemas.

Saludos,
Sistema Clínica PC
            """.strip()
        )
        
        if result['success']:
            print("✅ TEST EXITOSO - Email enviado")
            print("📨 Revisa tu bandeja de entrada")
            return True
        else:
            print(f"❌ Error: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    configurar_email_brevo()
    
    print("\n" + "="*50)
    respuesta = input("¿Quieres probar la nueva configuración? (s/n): ")
    if respuesta.lower() == 's':
        test_nueva_configuracion()
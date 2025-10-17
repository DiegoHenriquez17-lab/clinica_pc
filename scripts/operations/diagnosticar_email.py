"""
🔍 Diagnóstico completo de configuración de email
Verifica qué cuentas están configuradas y por qué no llegan los emails
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

from django.conf import settings

def diagnosticar_configuracion():
    """Diagnostica la configuración actual de email"""
    print("🔍 DIAGNÓSTICO COMPLETO DE EMAIL")
    print("=" * 50)
    
    # Verificar configuraciones
    print("📧 CONFIGURACIÓN ACTUAL:")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Verificar Brevo
    brevo_key = os.getenv('BREVO_API_KEY')
    print(f"\n🚀 BREVO API:")
    print(f"   API Key configurada: {'✅ SÍ' if brevo_key else '❌ NO'}")
    if brevo_key:
        print(f"   Clave: {brevo_key[:20]}...")
    
    # Probar conexión con Brevo
    if brevo_key:
        print(f"\n🧪 PROBANDO BREVO...")
        try:
            import requests
            
            headers = {
                'Accept': 'application/json',
                'api-key': brevo_key
            }
            
            # Verificar cuenta Brevo
            response = requests.get(
                "https://api.brevo.com/v3/account",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                account_info = response.json()
                print("✅ Conexión Brevo exitosa")
                print(f"   Email de la cuenta Brevo: {account_info.get('email', 'No disponible')}")
                print(f"   Nombre de la cuenta: {account_info.get('firstName', '')} {account_info.get('lastName', '')}")
                
                # Verificar límites
                print(f"\n📊 LÍMITES BREVO:")
                plan = account_info.get('plan', [{}])
                if plan:
                    daily_limit = plan[0].get('creditsLimit', {}).get('dailyLimit', 'No limitado')
                    print(f"   Límite diario: {daily_limit}")
                
                return account_info.get('email')
                
            else:
                print(f"❌ Error Brevo: {response.status_code}")
                print(f"   Mensaje: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error conectando a Brevo: {str(e)}")
            return None
    
    return None

def test_envio_directo():
    """Prueba envío directo especificando el remitente correcto"""
    print(f"\n📧 TEST DE ENVÍO DIRECTO")
    print("=" * 50)
    
    brevo_email = diagnosticar_configuracion()
    
    if not brevo_email:
        print("❌ No se pudo obtener el email de Brevo")
        return False
    
    # Email de destino
    email_destino = "diegohen2005gonzales@gmail.com"
    print(f"📤 Enviando desde: {brevo_email}")
    print(f"📥 Enviando hacia: {email_destino}")
    
    try:
        from gestion_clinica.email_services import BrevoEmailSender
        
        brevo_key = os.getenv('BREVO_API_KEY')
        sender = BrevoEmailSender(brevo_key)
        
        # Configurar email de prueba
        subject = "🧪 Test Directo - Clínica PC"
        message = f"""
¡Hola!

Este es un email de prueba enviado directamente desde Brevo.

CONFIGURACIÓN DETECTADA:
- Sistema: clinica.pc.inacap@gmail.com
- Brevo: {brevo_email}

Si recibes este email, la configuración está funcionando.

¿Está llegando a tu bandeja de entrada o spam?

Saludos,
Sistema de Prueba Clínica PC
        """.strip()
        
        print("🔄 Enviando email de prueba...")
        
        result = sender.send_email(
            to_email=email_destino,
            subject=subject,
            message=message
        )
        
        if result['success']:
            print("✅ EMAIL ENVIADO EXITOSAMENTE")
            print(f"📨 ID del mensaje: {result.get('message_id', 'N/A')}")
            print("\n💡 INSTRUCCIONES:")
            print("   1. Revisa tu bandeja de entrada")
            print("   2. Revisa tu carpeta de SPAM/JUNK")
            print("   3. Si no llega, el problema puede ser:")
            print("      - Email de Brevo diferente al sistema")
            print("      - Filtros de spam del proveedor")
            print("      - Configuración de Brevo")
            return True
        else:
            print(f"❌ Error: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return False

if __name__ == "__main__":
    test_envio_directo()
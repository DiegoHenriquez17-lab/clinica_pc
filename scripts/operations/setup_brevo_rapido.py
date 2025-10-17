"""
🚀 Configuración automática con nueva API Key
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')

# La API Key nunca debe hardcodearse; usar .env
NUEVA_API_KEY = os.getenv("BREVO_API_KEY", "")

def configurar_nueva_cuenta():
    """Configura automáticamente la nueva cuenta"""
    print("🚀 CONFIGURANDO NUEVA CUENTA BREVO")
    print("=" * 50)
    print("📧 Brevo es un servicio gratuito que usa HTTPS APIs")
    print("   ✅ 300 emails gratis por día")
    print("   ✅ Más confiable que SMTP")
    print("   ✅ No bloquean firewalls")
    print()
    
    # Verificar si ya está configurado
    brevo_key = os.getenv('BREVO_API_KEY')
    if brevo_key and brevo_key != 'tu-clave-api-brevo':
        print(f"✅ Brevo ya configurado: {brevo_key[:10]}...")
        return test_brevo(brevo_key)
    
    print("🔧 PASOS PARA CONFIGURAR BREVO:")
    print()
    print("1. Ve a: https://www.brevo.com/")
    print("2. Haz clic en 'Sign up free'")
    print("3. Completa el registro")
    print("4. Ve a 'Account' > 'SMTP & API'")
    print("5. Haz clic en 'Generate API Key'")
    print("6. Copia la clave")
    print("7. Pégala en tu archivo .env como:")
    print("   BREVO_API_KEY=tu-clave-real")
    print()
    
    # Opción interactiva
    response = input("¿Ya tienes la API Key de Brevo? (s/n): ").lower().strip()
    
    if response == 's':
        api_key = input("Pega tu API Key de Brevo: ").strip()
        
        if api_key:
            # Actualizar .env
            update_env_file(api_key)
            print("✅ API Key guardada en .env")
            return test_brevo(api_key)
        else:
            print("❌ No se proporcionó API Key")
    
    return False

def update_env_file(api_key):
    """Actualiza el archivo .env con la API key"""
    env_path = Path('.env')
    
    if env_path.exists():
        # Leer contenido actual
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Actualizar o agregar BREVO_API_KEY
        if 'BREVO_API_KEY=' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('BREVO_API_KEY='):
                    lines[i] = f'BREVO_API_KEY={api_key}'
                    break
            content = '\n'.join(lines)
        else:
            content += f'\n\n# Brevo API Key\nBREVO_API_KEY={api_key}\n'
        
        # Escribir archivo actualizado
        with open(env_path, 'w') as f:
            f.write(content)
    else:
        # Crear nuevo archivo .env
        with open(env_path, 'w') as f:
            f.write(f'BREVO_API_KEY={api_key}\n')

def test_brevo(api_key):
    """Prueba la configuración de Brevo"""
    print("\n🧪 Probando Brevo...")
    
    try:
        import requests
        
        # Test básico de conexión
        headers = {
            'Accept': 'application/json',
            'api-key': api_key
        }
        
        response = requests.get(
            'https://api.brevo.com/v3/account',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account_info = response.json()
            print(f"✅ Conexión exitosa con Brevo")
            print(f"📧 Email: {account_info.get('email', 'N/A')}")
            print(f"📊 Plan: {account_info.get('plan', {}).get('type', 'N/A')}")
            
            # Test de envío
            return test_send_email(api_key)
        else:
            print(f"❌ Error conectando con Brevo: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando Brevo: {str(e)}")
        return False

def test_send_email(api_key):
    """Prueba envío de email con Brevo"""
    print("\n📧 Probando envío de email...")
    
    try:
        import requests
        from django.conf import settings
        
        # Email de prueba
        test_email = settings.EMAIL_HOST_USER
        
        payload = {
            "sender": {
                "name": "Clinica PC - Test",
                "email": test_email
            },
            "to": [
                {
                    "email": test_email,
                    "name": "Usuario Test"
                }
            ],
            "subject": "🧪 Test Brevo - Sistema Clínica PC",
            "textContent": """
¡Excelente! 🎉

Este email de prueba confirma que Brevo está funcionando correctamente.

El sistema de email robusto ahora puede usar Brevo como alternativa 
cuando Gmail tenga problemas de conectividad.

Características:
✅ 300 emails gratis por día
✅ APIs HTTPS confiables  
✅ No bloqueado por firewalls
✅ Envío instantáneo

¡Tu sistema de boletas ya no tendrá más problemas de timeout!

Saludos,
Sistema Clínica PC
            """.strip()
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'api-key': api_key
        }
        
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Email enviado exitosamente!")
            print(f"📧 ID del mensaje: {result.get('messageId')}")
            print(f"📬 Revisa tu bandeja: {test_email}")
            return True
        else:
            print(f"❌ Error enviando email: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en envío: {str(e)}")
        return False

def main():
    print("🚀 SOLUCIONADOR DE PROBLEMAS DE CONECTIVIDAD")
    print("=" * 50)
    print()
    print("❌ Problema detectado: WinError 10060 (Timeout de conexión)")
    print("✅ Solución: Configurar Brevo (APIs HTTPS más confiables)")
    print()
    
    if configurar_nueva_cuenta():
        print("\n🎉 ¡PROBLEMA RESUELTO!")
        print("   Brevo configurado y funcionando")
        print("   Las boletas ahora se enviarán sin problemas")
        print()
        print("💡 Próximos pasos:")
        print("   1. Prueba enviando una boleta desde la web")
        print("   2. El sistema usará Brevo automáticamente")
        print("   3. Si tienes boletas pendientes, ejecuta:")
        print("      python manage.py reenviar_boletas_pendientes")
    else:
        print("\n⚠️ Configuración pendiente")
        print("   Sigue los pasos mostrados arriba")
        print("   Una vez configurado, no tendrás más timeouts")

if __name__ == "__main__":
    main()
"""
🔄 Actualizador para nueva cuenta de Brevo
Configura el sistema con la nueva API Key de clinica.pc.inacap@gmail.com
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

def actualizar_configuracion_brevo(nueva_api_key):
    """Actualiza la configuración con la nueva API key"""
    print("🔄 ACTUALIZANDO CONFIGURACIÓN BREVO")
    print("=" * 50)
    
    # Actualizar archivo .env
    env_path = os.path.join(BASE_DIR, '.env')
    
    env_content = f"""# Configuración de Email con Brevo
BREVO_API_KEY={nueva_api_key}

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=clinica.pc.inacap@gmail.com
EMAIL_HOST_PASSWORD=dummy

# Configuración adicional
DEBUG=True
SECRET_KEY=django-insecure-tu-clave-secreta
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Archivo .env actualizado")
    print("📧 Email configurado: clinica.pc.inacap@gmail.com")
    print(f"🔑 API Key configurada: {nueva_api_key[:20]}...")
    
    return True

def test_nueva_configuracion(api_key):
    """Prueba la nueva configuración"""
    print("\n🧪 PROBANDO NUEVA CONFIGURACIÓN")
    print("=" * 50)
    
    try:
        import requests
        
        headers = {
            'Accept': 'application/json',
            'api-key': api_key
        }
        
        # Verificar cuenta
        print("🔍 Verificando nueva cuenta Brevo...")
        response = requests.get(
            "https://api.brevo.com/v3/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account_info = response.json()
            email = account_info.get('email', 'No disponible')
            nombre = account_info.get('firstName', '') + ' ' + account_info.get('lastName', '')
            
            print("✅ Conexión exitosa a nueva cuenta Brevo")
            print(f"📧 Email de la cuenta: {email}")
            print(f"👤 Nombre: {nombre.strip()}")
            
            if email == "clinica.pc.inacap@gmail.com":
                print("🎯 ¡PERFECTO! La cuenta coincide con el sistema")
                
                # Test de envío
                print("\n📤 Enviando email de prueba...")
                
                from gestion_clinica.email_services import BrevoEmailSender
                sender = BrevoEmailSender(api_key)
                
                result = sender.send_email(
                    to_email="diegohen2005gonzales@gmail.com",
                    subject="✅ Nueva Cuenta Brevo - Clínica PC",
                    message="""
¡Excelente!

La nueva cuenta de Brevo está funcionando perfectamente:

✅ Cuenta Brevo: clinica.pc.inacap@gmail.com
✅ Sistema: clinica.pc.inacap@gmail.com
✅ TODO COINCIDE PERFECTAMENTE

Ahora las boletas deberían llegar sin problemas.

Saludos,
Sistema Clínica PC
                    """.strip()
                )
                
                if result['success']:
                    print("🎉 ¡EMAIL DE PRUEBA ENVIADO EXITOSAMENTE!")
                    print("📨 Revisa tu bandeja de entrada")
                    print("\n🚀 SISTEMA LISTO PARA USAR")
                    return True
                else:
                    print(f"❌ Error enviando email: {result['message']}")
            else:
                print(f"⚠️  La cuenta ({email}) no coincide con clinica.pc.inacap@gmail.com")
                print("   Asegúrate de haber creado la cuenta con el email correcto")
        else:
            print(f"❌ Error verificando cuenta: {response.status_code}")
            print(f"   Mensaje: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

def main():
    """Función principal"""
    print("🎯 CONFIGURADOR PARA NUEVA CUENTA BREVO")
    print("=" * 60)
    print("Este script configura el sistema con tu nueva cuenta de Brevo")
    print("📧 Email esperado: clinica.pc.inacap@gmail.com")
    print()
    
    # Solicitar API Key
    print("🔑 Ingresa la nueva API Key de Brevo:")
    print("   (Debe empezar con 'xkeysib-')")
    api_key = input("API Key: ").strip()
    
    if not api_key.startswith('xkeysib-'):
        print("❌ API Key inválida. Debe empezar con 'xkeysib-'")
        return
    
    if len(api_key) < 50:
        print("❌ API Key muy corta. Verifica que sea correcta")
        return
    
    print(f"\n✅ API Key válida: {api_key[:20]}...")
    
    # Actualizar configuración
    if actualizar_configuracion_brevo(api_key):
        print("\n🧪 ¿Quieres probar la nueva configuración? (s/n): ", end="")
        respuesta = input().strip().lower()
        
        if respuesta == 's':
            # Establecer variable de entorno temporalmente
            os.environ['BREVO_API_KEY'] = api_key
            test_nueva_configuracion(api_key)
        
        print("\n" + "="*60)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("   1. Reinicia el servidor Django")
        print("   2. Prueba enviando una boleta")
        print("   3. Los emails ahora deberían llegar perfectamente")
        print()
        print("💡 Si aún no llegan, revisa la carpeta de SPAM")

if __name__ == "__main__":
    main()
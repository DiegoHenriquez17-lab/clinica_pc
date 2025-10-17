"""
🎉 CONFIGURACIÓN INMEDIATA - NUEVA CUENTA BREVO
Configura automáticamente con la nueva API Key de clinica.pc.inacap@gmail.com
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')

# La API Key debe venir de variables de entorno (.env)
NUEVA_API_KEY = os.getenv("BREVO_API_KEY", "")

def configurar_sistema():
    """Configura el sistema con la nueva API Key"""
    print("🎯 CONFIGURANDO SISTEMA CON NUEVA API KEY")
    print("=" * 50)
    
    # 1. Crear/actualizar .env
    env_path = os.path.join(BASE_DIR, '.env')
    env_content = f"""# ✅ NUEVA CONFIGURACIÓN BREVO - clinica.pc.inacap@gmail.com
BREVO_API_KEY={NUEVA_API_KEY or 'tu-clave-real'}

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
    
    # 2. Corregir settings.py si es necesario
    settings_path = os.path.join(BASE_DIR, 'gestion_clinica', 'settings.py')
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        cambios_hechos = False
        
        # Corregir email si está mal
        if 'dg1604719@gmail.com' in settings_content:
            print("🔄 Corrigiendo email en settings.py...")
            settings_content = settings_content.replace(
                'dg1604719@gmail.com',
                'clinica.pc.inacap@gmail.com'
            )
            cambios_hechos = True
        
        if cambios_hechos:
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(settings_content)
            print("✅ Settings.py actualizado")
        else:
            print("✅ Settings.py ya está correcto")
    
    except Exception as e:
        print(f"⚠️  Advertencia settings.py: {str(e)}")
    
    # 3. Establecer variable de entorno
    if NUEVA_API_KEY:
        os.environ['BREVO_API_KEY'] = NUEVA_API_KEY
    
    print("🔑 Variable de entorno establecida")
    
    return True

def verificar_cuenta():
    """Verifica que la nueva cuenta esté funcionando"""
    print("\n🔍 VERIFICANDO NUEVA CUENTA")
    print("=" * 50)
    
    try:
        import requests
        
        headers = {
            'Accept': 'application/json',
            'api-key': NUEVA_API_KEY
        }
        
        print("🌐 Conectando a Brevo...")
        response = requests.get(
            "https://api.brevo.com/v3/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account_info = response.json()
            email = account_info.get('email', 'No disponible')
            nombre = account_info.get('firstName', '') + ' ' + account_info.get('lastName', '')
            
            print("✅ Conexión exitosa a Brevo")
            print(f"📧 Email de la cuenta: {email}")
            print(f"👤 Nombre: {nombre.strip()}")
            
            # Verificar límites
            plan = account_info.get('plan', [{}])
            if plan:
                daily_limit = plan[0].get('creditsLimit', {}).get('dailyLimit', 'Ilimitado')
                print(f"📊 Límite diario: {daily_limit}")
            
            if email == "clinica.pc.inacap@gmail.com":
                print("🎯 ¡PERFECTO! Email coincide exactamente")
                return True
            else:
                print(f"⚠️  Email no coincide: {email}")
                print("   Esperado: clinica.pc.inacap@gmail.com")
                return False
                
        else:
            print(f"❌ Error conectando: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def enviar_email_prueba():
    """Envía un email de prueba"""
    print("\n📤 ENVIANDO EMAIL DE PRUEBA")
    print("=" * 50)
    
    try:
        django.setup()
        from gestion_clinica.email_services import BrevoEmailSender
        
        if not NUEVA_API_KEY:
            print("❌ BREVO_API_KEY no está configurada. Defínela en .env")
            return False
        sender = BrevoEmailSender(NUEVA_API_KEY)
        
        print("🚀 Preparando email...")
        
        result = sender.send_email(
            to_email="diegohen2005gonzales@gmail.com",
            subject="🎉 ¡NUEVA CUENTA BREVO LISTA! - Clínica PC",
            message="""
¡EXCELENTES NOTICIAS! 🎉

Tu nueva cuenta de Brevo está configurada y funcionando perfectamente:

✅ Cuenta: clinica.pc.inacap@gmail.com
✅ API Key: Configurada y funcionando
✅ Sistema: Completamente sincronizado

🚀 ¿QUÉ SIGNIFICA ESTO?
- Las boletas ahora llegarán SIN PROBLEMAS
- No más timeouts de email  
- Remitente profesional y correcto
- 300 emails gratis por día

🔧 PRÓXIMOS PASOS:
1. Reinicia el servidor Django
2. Ve a la interfaz web
3. Envía una boleta de prueba
4. ¡Debería llegar perfectamente!

Si recibes este email, TODO ESTÁ FUNCIONANDO 🎯

Saludos,
Sistema Clínica PC - ¡PROBLEMA RESUELTO!
            """.strip()
        )
        
        if result['success']:
            print("🎉 ¡EMAIL ENVIADO EXITOSAMENTE!")
            print(f"📨 ID del mensaje: {result.get('message_id', 'N/A')}")
            print("✅ Revisa tu bandeja de entrada")
            return True
        else:
            print(f"❌ Error enviando: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🎯 CONFIGURACIÓN AUTOMÁTICA NUEVA CUENTA BREVO")
    print("=" * 60)
    print("📧 Nueva cuenta: clinica.pc.inacap@gmail.com")
    print(f"🔑 API Key: {(NUEVA_API_KEY[:20] + '...') if NUEVA_API_KEY else 'NO CONFIGURADA'}")
    print()
    
    # Paso 1: Configurar sistema
    if not configurar_sistema():
        print("❌ Error en configuración")
        return
    
    # Paso 2: Verificar cuenta
    if not verificar_cuenta():
        print("❌ Error verificando cuenta")
        return
    
    # Paso 3: Enviar email de prueba
    if enviar_email_prueba():
        print("\n" + "="*60)
        print("🏆 ¡CONFIGURACIÓN COMPLETADA CON ÉXITO!")
        print()
        print("🎉 RESUMEN:")
        print("   ✅ Nueva API Key configurada")
        print("   ✅ Email correcto: clinica.pc.inacap@gmail.com") 
        print("   ✅ Cuenta Brevo verificada")
        print("   ✅ Email de prueba enviado")
        print()
        print("🚀 ¿QUÉ SIGUE?")
        print("   1. Reinicia el servidor Django")
        print("   2. Prueba enviando una boleta")
        print("   3. ¡Los emails deberían llegar sin problemas!")
        print()
        print("💡 Si no llega el email de prueba, revisa SPAM")
    else:
        print("\n⚠️  Configuración aplicada pero hay problemas con el envío")
        print("   Reinicia Django y prueba desde la interfaz web")

if __name__ == "__main__":
    main()
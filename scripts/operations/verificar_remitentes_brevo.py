"""
🔍 Verificador de dominios y remitentes en Brevo
Revisa qué remitentes están autorizados en tu cuenta Brevo
"""
import os
import requests

def verificar_remitentes_brevo():
    """Verifica qué remitentes están configurados en Brevo"""
    print("🔍 VERIFICANDO REMITENTES EN BREVO")
    print("=" * 50)
    
    brevo_key = os.getenv('BREVO_API_KEY')
    if not brevo_key:
        print("❌ No hay API key de Brevo configurada")
        return
    
    headers = {
        'Accept': 'application/json',
        'api-key': brevo_key
    }
    
    try:
        # Verificar remitentes
        print("📧 Consultando remitentes autorizados...")
        response = requests.get(
            "https://api.brevo.com/v3/senders",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            senders = response.json()
            print("✅ Remitentes encontrados:")
            
            for sender in senders.get('senders', []):
                name = sender.get('name', 'Sin nombre')
                email = sender.get('email', 'Sin email')
                active = sender.get('active', False)
                status = "✅ ACTIVO" if active else "❌ INACTIVO"
                
                print(f"   • {name} <{email}> - {status}")
                
                # Verificar si es nuestro email objetivo
                if email == "clinica.pc.inacap@gmail.com":
                    print("     🎯 ¡Este es el email que queremos usar!")
                    if not active:
                        print("     ⚠️  PERO NO ESTÁ ACTIVO")
            
            # Verificar si podemos agregar el remitente
            if not any(s.get('email') == 'clinica.pc.inacap@gmail.com' for s in senders.get('senders', [])):
                print("\n💡 SOLUCIÓN:")
                print("   El email clinica.pc.inacap@gmail.com NO está en Brevo")
                print("   Opciones:")
                print("   1. Agregar el email a Brevo como remitente verificado")
                print("   2. Usar el email de Brevo (dg1604719@gmail.com)")
                print("   3. Cambiar de cuenta de Brevo")
                
        else:
            print(f"❌ Error consultando remitentes: {response.status_code}")
            print(f"   Mensaje: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def agregar_remitente_brevo():
    """Intenta agregar el remitente deseado a Brevo"""
    print("\n🔧 INTENTANDO AGREGAR REMITENTE")
    print("=" * 50)
    
    brevo_key = os.getenv('BREVO_API_KEY')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'api-key': brevo_key
    }
    
    # Datos del remitente
    sender_data = {
        "name": "Clínica PC",
        "email": "clinica.pc.inacap@gmail.com"
    }
    
    try:
        print("📤 Enviando solicitud para agregar remitente...")
        response = requests.post(
            "https://api.brevo.com/v3/senders",
            headers=headers,
            json=sender_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ ¡Remitente agregado exitosamente!")
            print("📧 Ahora clinica.pc.inacap@gmail.com está disponible")
            print("⏳ Puede requerir verificación por email")
        elif response.status_code == 400:
            error_data = response.json()
            print("⚠️  No se pudo agregar el remitente:")
            print(f"   Razón: {error_data.get('message', 'Error desconocido')}")
            print("💡 Posibles causas:")
            print("   - El email ya existe")
            print("   - El dominio no está verificado")
            print("   - Se requiere verificación manual")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Mensaje: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    verificar_remitentes_brevo()
    
    print("\n" + "="*50)
    respuesta = input("¿Intentar agregar clinica.pc.inacap@gmail.com como remitente? (s/n): ")
    if respuesta.lower() == 's':
        agregar_remitente_brevo()
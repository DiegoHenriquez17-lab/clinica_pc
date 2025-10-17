"""
⚡ Solución temporal - Usar cuenta Brevo actual
Cambia temporalmente para usar dg1604719@gmail.com hasta crear la nueva cuenta
"""
import os

def solucion_temporal():
    """Aplica solución temporal usando la cuenta actual de Brevo"""
    print("⚡ SOLUCIÓN TEMPORAL")
    print("=" * 50)
    print("Usando cuenta actual: dg1604719@gmail.com")
    print("Los emails llegarán AHORA, pero desde esta cuenta")
    print()
    
    # Cambiar settings.py
    settings_path = r'c:\Users\diego\Downloads\clinica_pc\gestion_clinica\settings.py'
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cambios temporales
        new_content = content.replace(
            'DEFAULT_FROM_EMAIL = "Clínica PC <clinica.pc.inacap@gmail.com>"',
            'DEFAULT_FROM_EMAIL = "Clínica PC <dg1604719@gmail.com>"'
        )
        
        new_content = new_content.replace(
            'EMAIL_HOST_USER = "clinica.pc.inacap@gmail.com"',
            'EMAIL_HOST_USER = "dg1604719@gmail.com"'
        )
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Cambios aplicados temporalmente")
        print("📧 Remitente temporal: dg1604719@gmail.com")
        print("🔄 Reinicia el servidor Django")
        print()
        print("⚠️  RECUERDA: Esto es temporal")
        print("   Cuando crees la nueva cuenta, ejecuta:")
        print("   python actualizar_brevo_nueva_cuenta.py")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    solucion_temporal()
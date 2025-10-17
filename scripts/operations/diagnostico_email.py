#!/usr/bin/env python
"""
Script de diagnóstico para encontrar el problema con el envío de emails
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clinica.settings')
django.setup()

def test_basic_email():
    """Prueba básica de envío de email"""
    print("🔍 Probando configuración básica de email...")
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        
        resultado = send_mail(
            subject='🧪 Test Email - Clínica PC',
            message='Este es un email de prueba. Si lo recibes, la configuración básica funciona.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['clinica.pc.inacap@gmail.com'],
            fail_silently=False,
        )
        
        if resultado == 1:
            print("✅ Email básico enviado correctamente")
            return True
        else:
            print("❌ Error: Email no se pudo enviar")
            return False
            
    except Exception as e:
        print(f"❌ Error en email básico: {str(e)}")
        return False

def test_selenium():
    """Prueba si Selenium funciona"""
    print("\n🔍 Probando Selenium...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Configurar Chrome en modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("📥 Instalando/verificando ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("🚀 Abriendo Chrome headless...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("🌐 Probando navegación...")
        driver.get("http://127.0.0.1:8000/recepcion/boleta-pdf/1/")
        
        print(f"📄 Título de página: {driver.title}")
        
        driver.quit()
        print("✅ Selenium funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en Selenium: {str(e)}")
        return False

def test_full_pdf_generation():
    """Prueba la generación completa de PDF"""
    print("\n🔍 Probando generación de PDF...")
    try:
        from recepcion.models import Equipo
        from recepcion.views import generar_boleta_pdf
        
        # Buscar un equipo para probar
        equipo = Equipo.objects.first()
        if not equipo:
            print("❌ No hay equipos en la base de datos para probar")
            return False
            
        print(f"📋 Probando con equipo #{equipo.id}")
        
        pdf_content = generar_boleta_pdf(equipo)
        
        if pdf_content and len(pdf_content) > 1000:  # PDF válido debe tener al menos 1KB
            print(f"✅ PDF generado correctamente ({len(pdf_content)} bytes)")
            return True
        else:
            print("❌ PDF no se generó o es muy pequeño")
            return False
            
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        return False

def main():
    print("🚀 DIAGNÓSTICO DEL SISTEMA DE EMAIL - CLÍNICA PC")
    print("=" * 60)
    
    # Test 1: Email básico
    email_ok = test_basic_email()
    
    # Test 2: Selenium
    selenium_ok = test_selenium()
    
    # Test 3: Generación de PDF
    pdf_ok = test_full_pdf_generation()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO:")
    print(f"📧 Email básico: {'✅ OK' if email_ok else '❌ FALLA'}")
    print(f"🤖 Selenium: {'✅ OK' if selenium_ok else '❌ FALLA'}")
    print(f"📄 Generación PDF: {'✅ OK' if pdf_ok else '❌ FALLA'}")
    
    if email_ok and selenium_ok and pdf_ok:
        print("\n🎉 ¡Todo funciona! El problema debe ser otro.")
    else:
        print("\n🔧 Problemas encontrados. Revisar los errores arriba.")

if __name__ == '__main__':
    main()
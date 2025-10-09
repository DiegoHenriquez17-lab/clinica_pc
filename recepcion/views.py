from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from io import BytesIO
from .models import Cliente, Equipo, Estudiante, TrazaEquipo
from login_app.permissions import role_required
from datetime import timedelta
import json
import tempfile
import os
import time


@role_required('recepcion')
def index(request):
    """Vista principal de recepción con formulario de registro"""
    if request.method == 'POST':
        return registrar_equipo(request)
    
    # Estadísticas para mostrar en la sidebar
    hoy = timezone.now().date()
    ingresos_hoy = Equipo.objects.filter(created_at__date=hoy).count()
    ultimos_ingresos = Equipo.objects.select_related('cliente').order_by('-created_at')[:5]
    clientes_recientes = Cliente.objects.order_by('-created_at')[:5]
    
    context = {
        'ingresos_hoy': ingresos_hoy,
        'ultimos_ingresos': ultimos_ingresos,
        'clientes_recientes': clientes_recientes,
    }
    
    return render(request, 'recepcion/index.html', context)


def registrar_equipo(request):
    """Procesa el formulario de registro de equipos"""
    try:
        # Datos del cliente
        nombre_cliente = request.POST.get('nombre_cliente', '').strip()
        rut_cliente = request.POST.get('rut_cliente', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        imagen_carnet = request.FILES.get('imagen_carnet')
        
        # Datos del equipo
        tipo_equipo = request.POST.get('tipo_equipo', '').strip()
        marca = request.POST.get('marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        serial = request.POST.get('serial', '').strip()
        problema = request.POST.get('problema', '').strip()
        
        # Nuevos campos mejorados
        relato_cliente = request.POST.get('relato_cliente', '').strip()
        observaciones_recepcionista = request.POST.get('observaciones_recepcionista', '').strip()
        caja_cliente = request.POST.get('caja_cliente', '').strip()
        caja_equipo = request.POST.get('caja_equipo', '').strip()
        
        observaciones_adicionales = request.POST.get('observaciones_adicionales', '').strip()
        
        # Accesorios (checkbox múltiple)
        accesorios = request.POST.getlist('accesorios')
        
        if not nombre_cliente or not telefono or not tipo_equipo or not relato_cliente:
            messages.error(request, 'Por favor complete todos los campos obligatorios: Nombre, Teléfono, Tipo de Equipo y Relato del Cliente.')
            return redirect('recepcion:index')
        
        # Crear o obtener cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre_cliente,
            defaults={
                'rut': rut_cliente or None,
                'telefono': telefono,
                'correo': correo or None,
                'ciudad': ciudad or None,
                'imagen_carnet': imagen_carnet,
            }
        )
        
        # Si el cliente ya existe pero tiene datos diferentes, actualizar
        if not created:
            if rut_cliente and cliente.rut != rut_cliente:
                cliente.rut = rut_cliente
            if telefono and cliente.telefono != telefono:
                cliente.telefono = telefono
            if correo and cliente.correo != correo:
                cliente.correo = correo
            if ciudad and cliente.ciudad != ciudad:
                cliente.ciudad = ciudad
            if imagen_carnet and not cliente.imagen_carnet:
                cliente.imagen_carnet = imagen_carnet
            cliente.save()
        
        # Crear equipo
        equipo = Equipo.objects.create(
            cliente=cliente,
            tipo_equipo=tipo_equipo,
            marca=marca or None,
            modelo=modelo or None,
            serial=serial or None,
            problema=problema,
            relato_cliente=relato_cliente,
            observaciones_recepcionista=observaciones_recepcionista,
            caja_cliente=caja_cliente,
            caja_equipo=caja_equipo,
            accesorios=accesorios,
            observaciones_adicionales=observaciones_adicionales or None,
            estado='recepcion'
        )
        
        # Crear traza de ingreso
        TrazaEquipo.objects.create(
            equipo=equipo,
            accion='ingreso',
            descripcion=f'Equipo ingresado al sistema. Relato del cliente: {relato_cliente[:100]}...',
            usuario=request.user
        )
        
        messages.success(request, f'Equipo registrado exitosamente. ID: #{equipo.id}')
        return redirect('recepcion:index')
        
    except Exception as e:
        messages.error(request, f'Error al registrar el equipo: {str(e)}')
        return redirect('recepcion:index')


@role_required('recepcion')
def ver_cliente(request, cliente_id):
    """Vista para mostrar información completa del cliente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    equipos = cliente.equipos.all().order_by('-created_at')
    
    context = {
        'cliente': cliente,
        'equipos': equipos,
    }
    
    return render(request, 'recepcion/ver_cliente.html', context)


def generar_boleta_pdf(equipo):
    """Genera un PDF optimizado usando Selenium con configuraciones de velocidad"""
    
    try:
        # Configurar Chrome en modo headless ULTRA RÁPIDO
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Nuevo modo headless más rápido
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # No cargar imágenes externas (solo las del servidor)
        chrome_options.add_argument('--disable-javascript')  # Desactivar JS innecesario
        chrome_options.add_argument('--window-size=1024,768')  # Ventana más pequeña
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # Configurar timeouts agresivos
        chrome_options.add_argument('--dom-automation-controller')
        
        # Crear driver con cache de ChromeDriverManager (solo descarga una vez)
        try:
            service = Service(ChromeDriverManager(cache_valid_range=30).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Error con ChromeDriverManager: {e}")
            # Fallback: intentar con Chrome por defecto del sistema
            driver = webdriver.Chrome(options=chrome_options)
        
        # Configurar timeouts
        driver.set_page_load_timeout(10)  # Max 10 segundos para cargar
        driver.implicitly_wait(2)  # Max 2 segundos para encontrar elementos
        
        try:
            # Ir a la página de la boleta (versión sin autenticación)
            base_url = "http://127.0.0.1:8000"
            boleta_url = f"{base_url}/recepcion/boleta-pdf/{equipo.id}/"
            
            print(f"⚡ Generando PDF rápido para: {boleta_url}")
            start_time = time.time()
            
            driver.get(boleta_url)
            
            # Esperar MÍNIMO necesario - solo hasta que el body existe
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Script optimizado para preparar PDF
            script = """
            // Forzar que las imágenes se carguen inmediatamente
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                img.style.display = 'block';
                img.loading = 'eager';
            });
            
            // Limpiar para PDF en una sola pasada
            const elementsToHide = document.querySelectorAll('button, nav, aside, script');
            elementsToHide.forEach(el => el.remove());
            
            // Optimizar layout para PDF
            const main = document.querySelector('main');
            if (main) {
                main.style.cssText = 'width:100%!important;margin:0!important;padding:20px!important';
            }
            
            const boleta = document.querySelector('.bg-white');
            if (boleta) {
                boleta.style.cssText = 'border-radius:0!important;box-shadow:none!important;background:white!important';
            }
            
            // Marcar como listo
            document.body.setAttribute('data-pdf-ready', 'true');
            """
            
            driver.execute_script(script)
            
            # Esperar solo hasta que esté marcado como listo
            WebDriverWait(driver, 3).until(
                lambda d: d.find_element(By.TAG_NAME, "body").get_attribute("data-pdf-ready") == "true"
            )
            
            # Configurar opciones de impresión optimizadas
            print_options = {
                'paperWidth': 8.27,
                'paperHeight': 11.69,
                'marginTop': 0.4,
                'marginBottom': 0.4,
                'marginLeft': 0.4,
                'marginRight': 0.4,
                'printBackground': True,
                'preferCSSPageSize': False,
                'displayHeaderFooter': False,
                'generateTaggedPDF': False,  # Más rápido sin tags
                'transferMode': 'ReturnAsBase64'  # Más eficiente
            }
            
            # Generar PDF usando Chrome DevTools
            pdf_data = driver.execute_cdp_cmd('Page.printToPDF', print_options)
            
            # Decodificar el PDF desde base64
            pdf_bytes = base64.b64decode(pdf_data['data'])
            
            end_time = time.time()
            print(f"✅ PDF generado en {end_time - start_time:.2f} segundos")
            
            return pdf_bytes
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Error generando PDF con Selenium: {e}")
        # Fallback: usar método alternativo más simple
        return generar_boleta_pdf_fallback(equipo)


def generar_boleta_pdf_fallback(equipo):
    """Método fallback usando reportlab para generar PDF básico"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredText(width/2, height - inch, "CLÍNICA PC")
    p.setFont("Helvetica", 12)
    p.drawCentredText(width/2, height - inch*1.3, "Servicio Técnico Especializado")
    p.drawCentredText(width/2, height - inch*1.6, f"Boleta de Servicio #{equipo.id}")
    p.drawCentredText(width/2, height - inch*1.9, f"Fecha: {equipo.created_at.strftime('%d/%m/%Y %H:%M')}")
    
    # Información del cliente
    y_position = height - inch*2.5
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y_position, "DATOS DEL CLIENTE:")
    p.setFont("Helvetica", 10)
    y_position -= 20
    p.drawString(inch, y_position, f"Nombre: {equipo.cliente.nombre}")
    y_position -= 15
    p.drawString(inch, y_position, f"RUT: {equipo.cliente.rut or 'N/A'}")
    y_position -= 15
    p.drawString(inch, y_position, f"Teléfono: {equipo.cliente.telefono}")
    
    # Información del equipo
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y_position, "DATOS DEL EQUIPO:")
    p.setFont("Helvetica", 10)
    y_position -= 20
    p.drawString(inch, y_position, f"Tipo: {equipo.tipo_equipo}")
    y_position -= 15
    p.drawString(inch, y_position, f"Marca: {equipo.marca or 'N/A'}")
    y_position -= 15
    p.drawString(inch, y_position, f"Modelo: {equipo.modelo or 'N/A'}")
    
    # Problema reportado
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y_position, "PROBLEMA REPORTADO:")
    p.setFont("Helvetica", 10)
    y_position -= 20
    p.drawString(inch, y_position, equipo.problema[:80] + "..." if len(equipo.problema) > 80 else equipo.problema)
    
    # Firmas
    y_position = inch*2
    p.line(inch, y_position, inch*3, y_position)
    p.line(inch*4.5, y_position, inch*6.5, y_position)
    p.drawString(inch, y_position - 15, "Firma del Cliente")
    p.drawString(inch*4.5, y_position - 15, "Firma del Técnico")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()


def boleta_pdf_view(request, equipo_id):
    """Vista especial para mostrar la boleta sin autenticación (solo para generar PDF)"""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Obtener todos los datos necesarios igual que en la vista original
    from diagnostico.models import Diagnostico, ReparacionHardware, ReparacionSoftware
    
    # Obtener información relacionada (misma lógica que generar_boleta)
    diagnostico = None
    reparacion_hardware = None
    reparacion_software = None
    
    try:
        diagnostico = equipo.diagnostico
        if diagnostico.area_recomendada == 'hardware' and hasattr(diagnostico, 'reparacion_hardware'):
            reparacion_hardware = diagnostico.reparacion_hardware
        elif diagnostico.area_recomendada == 'software' and hasattr(diagnostico, 'reparacion_software'):
            reparacion_software = diagnostico.reparacion_software
    except Diagnostico.DoesNotExist:
        pass
    
    # Obtener traza del equipo
    trazas = TrazaEquipo.objects.filter(equipo=equipo).order_by('timestamp')
    
    context = {
        'equipo': equipo,
        'diagnostico': diagnostico,
        'reparacion_hardware': reparacion_hardware,
        'reparacion_software': reparacion_software,
        'trazas': trazas,
        'is_pdf_mode': True,  # Flag para indicar que es modo PDF
    }
    
    return render(request, 'boleta.html', context)


import threading

def enviar_boleta_asincrono(equipo, email_cliente):
    """Función para enviar la boleta en segundo plano"""
    try:
        print(f"🚀 Iniciando generación de PDF para boleta #{equipo.id}")
        
        # Generar PDF
        pdf_content = generar_boleta_pdf(equipo)
        
        if pdf_content:
            # Crear email
            subject = f'Boleta de Servicio #{equipo.id} - Clínica PC'
            message = f"""
Estimado/a {equipo.cliente.nombre},

Adjuntamos la boleta de servicio para su equipo {equipo.tipo_equipo} {equipo.marca} {equipo.modelo}.

Número de boleta: #{equipo.id}
Fecha de ingreso: {equipo.created_at.strftime('%d/%m/%Y')}

Saludos cordiales,
Equipo Clínica PC
            """.strip()
            
            email = EmailMessage(
                subject=subject,
                body=message,
                to=[email_cliente],
            )
            
            # Adjuntar PDF
            email.attach(f'boleta_{equipo.id}.pdf', pdf_content, 'application/pdf')
            
            # Enviar email
            email.send()
            
            print(f"✅ Boleta #{equipo.id} enviada exitosamente a {email_cliente}")
        else:
            print(f"❌ Error al generar PDF para boleta #{equipo.id}")
            
    except Exception as e:
        print(f"❌ Error enviando boleta #{equipo.id}: {str(e)}")


@role_required('recepcion')
def enviar_boleta_email(request, equipo_id):
    """Envía la boleta por email al cliente de forma asíncrona"""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        email_cliente = request.POST.get('email_cliente')
        
        if not email_cliente:
            messages.error(request, 'Debe proporcionar un email válido')
            return redirect('generar_boleta', equipo_id=equipo_id)
        
        try:
            # Iniciar el proceso en segundo plano
            thread = threading.Thread(
                target=enviar_boleta_asincrono,
                args=(equipo, email_cliente)
            )
            thread.daemon = True
            thread.start()
            
            # Respuesta inmediata al usuario
            messages.success(request, f'📧 La boleta está siendo procesada y se enviará a {email_cliente} en unos momentos...')
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
    
    return redirect('generar_boleta', equipo_id=equipo_id)


from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def detalle_equipo_ajax(request, equipo_id):
    """Vista AJAX para obtener detalles completos de un equipo"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Obtener trazas del equipo
        trazas = TrazaEquipo.objects.filter(equipo=equipo).order_by('-timestamp')
        
        # Renderizar template
        html = render_to_string('recepcion/detalle_equipo_ajax.html', {
            'equipo': equipo,
            'trazas': trazas,
        })
        
        return JsonResponse({
            'success': True,
            'html': html
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
"""
🚀 Utilidades para el manejo robusto de emails
Sistema con múltiples reintentos y proveedores de respaldo
"""
import time
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from typing import Optional, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Configurar logging
logger = logging.getLogger(__name__)

class EmailSenderRobust:
    """Clase para envío robusto de emails con reintentos y múltiples proveedores"""
    
    # Configuraciones de proveedores de respaldo
    PROVIDERS = {
        'gmail': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'timeout': 30
        },
        'outlook': {
            'host': 'smtp-mail.outlook.com', 
            'port': 587,
            'use_tls': True,
            'timeout': 30
        },
        'yahoo': {
            'host': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True,
            'timeout': 30
        }
    }
    
    def __init__(self):
        self.max_retries = getattr(settings, 'EMAIL_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'EMAIL_RETRY_DELAY', 5)
    
    def send_email_with_retry(self, 
                             subject: str, 
                             message: str, 
                             to_emails: List[str], 
                             attachment_data: Optional[bytes] = None,
                             attachment_name: str = 'attachment.pdf',
                             attachment_type: str = 'application/pdf') -> dict:
        """
        Envía un email con reintentos automáticos
        
        Returns:
            dict: {'success': bool, 'message': str, 'provider': str}
        """
        
        last_error = None
        
        # Intentar con Django EmailMessage (configuración actual)
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📧 Intento {attempt + 1}/{self.max_retries} enviando email con Django")
                
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    to=to_emails,
                )
                
                if attachment_data:
                    email.attach(attachment_name, attachment_data, attachment_type)
                
                email.send(fail_silently=False)
                
                logger.info(f"✅ Email enviado exitosamente con Django en intento {attempt + 1}")
                return {
                    'success': True,
                    'message': f'Email enviado exitosamente con Django (intento {attempt + 1})',
                    'provider': 'django'
                }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Intento {attempt + 1} falló con Django: {last_error}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"🔄 Esperando {self.retry_delay} segundos antes del siguiente intento...")
                    time.sleep(self.retry_delay)
        
        # Si Django falla, intentar con proveedores alternativos directamente
        logger.info("🔄 Django falló, intentando con proveedores alternativos...")
        
        for provider_name, config in self.PROVIDERS.items():
            try:
                result = self._send_with_smtp_direct(
                    subject, message, to_emails, 
                    attachment_data, attachment_name, attachment_type,
                    provider_name, config
                )
                if result['success']:
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Proveedor {provider_name} falló: {str(e)}")
                continue
        
        # Si todo falla
        error_msg = f"❌ Todos los proveedores fallaron. Último error: {last_error}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'message': error_msg,
            'provider': 'none'
        }
    
    def _send_with_smtp_direct(self, subject, message, to_emails, 
                              attachment_data, attachment_name, attachment_type,
                              provider_name, config):
        """Envía email directamente con SMTP (respaldo)"""
        
        logger.info(f"📧 Intentando envío directo con {provider_name}")
        
        # Crear mensaje MIME
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        # Adjuntar cuerpo del mensaje
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Adjuntar archivo si existe
        if attachment_data:
            attachment = MIMEApplication(attachment_data, _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
            msg.attach(attachment)
        
        # Conectar y enviar
        server = smtplib.SMTP(config['host'], config['port'])
        server.set_debuglevel(0)  # Cambiar a 1 para debug
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(settings.EMAIL_HOST_USER, to_emails, text)
        server.quit()
        
        logger.info(f"✅ Email enviado exitosamente con {provider_name}")
        return {
            'success': True,
            'message': f'Email enviado con {provider_name}',
            'provider': provider_name
        }


def send_boleta_email_robust(equipo_id: int, email_cliente: str, pdf_content: bytes) -> dict:
    """
    Función principal para envío de boletas con sistema robusto
    """
    try:
        sender = EmailSenderRobust()
        
        subject = f"Boleta de Recepción #{equipo_id} - Clínica PC"
        
        message = f"""
Estimado/a cliente,

Adjunto encontrará la boleta de recepción para su equipo #{equipo_id}.

Esta boleta confirma que hemos recibido su equipo y contiene toda la información 
relevante sobre el estado actual y los siguientes pasos.

Por favor, conserve esta boleta como comprobante de nuestro servicio.

Si tiene alguna pregunta, no dude en contactarnos.

Saludos cordiales,
Equipo Clínica PC
        """.strip()
        
        result = sender.send_email_with_retry(
            subject=subject,
            message=message,
            to_emails=[email_cliente],
            attachment_data=pdf_content,
            attachment_name=f'boleta_{equipo_id}.pdf'
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error crítico enviando boleta #{equipo_id}: {str(e)}")
        return {
            'success': False,
            'message': f'Error crítico: {str(e)}',
            'provider': 'error'
        }


# Función de respaldo para testing
def test_email_configuration():
    """Prueba la configuración de email actual"""
    try:
        from django.core.mail import send_mail
        
        send_mail(
            subject='Test - Configuración Email Clínica PC',
            message='Este es un email de prueba para verificar la configuración.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Enviar a sí mismo
            fail_silently=False,
        )
        
        return {'success': True, 'message': 'Configuración de email funcionando correctamente'}
        
    except Exception as e:
        return {'success': False, 'message': f'Error en configuración: {str(e)}'}
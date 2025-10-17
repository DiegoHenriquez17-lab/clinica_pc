"""
🚀 Configuración para servicios de email gratuitos alternativos
Brevo (SendinBlue), SendGrid, Mailgun - opciones gratuitas y robustas
"""
import os
import requests
import base64
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BrevoEmailSender:
    """
    Brevo (SendinBlue) - Servicio gratuito con 300 emails/día
    Muy confiable y fácil de configurar
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'api-key': api_key
        }
    
    def send_email(self, to_email: str, subject: str, message: str, 
                   attachment_data: Optional[bytes] = None, 
                   attachment_name: str = 'attachment.pdf') -> Dict:
        """Envía email usando la API de Brevo"""
        
        try:
            # Preparar el payload básico
            payload = {
                "sender": {
                    "name": "Clínica PC",
                    "email": os.getenv('EMAIL_HOST_USER', 'noreply@clinicapc.com')
                },
                "to": [
                    {
                        "email": to_email,
                        "name": "Cliente"
                    }
                ],
                "subject": subject,
                "textContent": message
            }
            
            # Agregar adjunto si existe
            if attachment_data:
                # Convertir a base64
                attachment_b64 = base64.b64encode(attachment_data).decode('utf-8')
                payload["attachment"] = [
                    {
                        "content": attachment_b64,
                        "name": attachment_name
                    }
                ]
            
            # Enviar via API
            response = requests.post(
                f"{self.base_url}/smtp/email",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Email enviado exitosamente via Brevo a {to_email}")
                return {
                    'success': True,
                    'message': 'Email enviado exitosamente via Brevo',
                    'provider': 'brevo',
                    'message_id': response.json().get('messageId')
                }
            else:
                error_msg = f"Error Brevo: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'provider': 'brevo'
                }
                
        except Exception as e:
            error_msg = f"Excepción en Brevo: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'provider': 'brevo'
            }


class SendGridEmailSender:
    """
    SendGrid - Servicio gratuito con 100 emails/día
    Muy profesional y confiable
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sendgrid.com/v3"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_email(self, to_email: str, subject: str, message: str,
                   attachment_data: Optional[bytes] = None,
                   attachment_name: str = 'attachment.pdf') -> Dict:
        """Envía email usando la API de SendGrid"""
        
        try:
            payload = {
                "personalizations": [
                    {
                        "to": [
                            {
                                "email": to_email
                            }
                        ]
                    }
                ],
                "from": {
                    "email": os.getenv('EMAIL_HOST_USER', 'noreply@clinicapc.com'),
                    "name": "Clínica PC"
                },
                "subject": subject,
                "content": [
                    {
                        "type": "text/plain",
                        "value": message
                    }
                ]
            }
            
            # Agregar adjunto si existe
            if attachment_data:
                attachment_b64 = base64.b64encode(attachment_data).decode('utf-8')
                payload["attachments"] = [
                    {
                        "content": attachment_b64,
                        "filename": attachment_name,
                        "type": "application/pdf",
                        "disposition": "attachment"
                    }
                ]
            
            response = requests.post(
                f"{self.base_url}/mail/send",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 202:
                logger.info(f"✅ Email enviado exitosamente via SendGrid a {to_email}")
                return {
                    'success': True,
                    'message': 'Email enviado exitosamente via SendGrid',
                    'provider': 'sendgrid'
                }
            else:
                error_msg = f"Error SendGrid: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'provider': 'sendgrid'
                }
                
        except Exception as e:
            error_msg = f"Excepción en SendGrid: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'provider': 'sendgrid'
            }


def get_available_email_services() -> List[Dict]:
    """Retorna lista de servicios de email configurados y disponibles"""
    
    services = []
    
    # Brevo (SendinBlue)
    brevo_api_key = os.getenv('BREVO_API_KEY')
    if brevo_api_key:
        services.append({
            'name': 'Brevo',
            'provider': 'brevo',
            'sender': BrevoEmailSender(brevo_api_key),
            'daily_limit': 300,
            'description': 'Servicio gratuito confiable con 300 emails/día'
        })
    
    # SendGrid
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_api_key:
        services.append({
            'name': 'SendGrid',
            'provider': 'sendgrid',
            'sender': SendGridEmailSender(sendgrid_api_key),
            'daily_limit': 100,
            'description': 'Servicio profesional con 100 emails/día'
        })
    
    return services


def send_email_with_fallback_services(to_email: str, subject: str, message: str,
                                     attachment_data: Optional[bytes] = None,
                                     attachment_name: str = 'attachment.pdf') -> Dict:
    """
    Intenta enviar email con servicios de respaldo en orden de prioridad
    """
    services = get_available_email_services()
    
    if not services:
        return {
            'success': False,
            'message': 'No hay servicios de email alternativos configurados',
            'provider': 'none'
        }
    
    last_error = None
    
    for service in services:
        try:
            logger.info(f"🔄 Intentando envío con {service['name']}")
            
            result = service['sender'].send_email(
                to_email=to_email,
                subject=subject,
                message=message,
                attachment_data=attachment_data,
                attachment_name=attachment_name
            )
            
            if result['success']:
                return result
            else:
                last_error = result['message']
                logger.warning(f"⚠️ {service['name']} falló: {last_error}")
                
        except Exception as e:
            last_error = str(e)
            logger.error(f"❌ Error con {service['name']}: {last_error}")
    
    return {
        'success': False,
        'message': f'Todos los servicios alternativos fallaron. Último error: {last_error}',
        'provider': 'all_failed'
    }
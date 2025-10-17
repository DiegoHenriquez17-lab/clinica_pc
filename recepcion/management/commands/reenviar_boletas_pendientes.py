"""
🚀 Comando para reenviar boletas pendientes
Uso: python manage.py reenviar_boletas_pendientes
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import glob
from gestion_clinica.email_services import send_email_with_fallback_services
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reenvía boletas que no se pudieron enviar por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limite',
            type=int,
            default=10,
            help='Número máximo de boletas a procesar'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo prueba - solo mostrar boletas pendientes sin enviar'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando reenvío de boletas pendientes...')
        )
        
        # Directorio de boletas pendientes
        pending_dir = os.path.join(settings.MEDIA_ROOT, 'boletas_pendientes')
        
        if not os.path.exists(pending_dir):
            self.stdout.write(
                self.style.WARNING('📁 No existe directorio de boletas pendientes')
            )
            return
        
        # Buscar archivos de información
        info_files = glob.glob(os.path.join(pending_dir, 'email_info_*.txt'))
        
        if not info_files:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay boletas pendientes de reenvío')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'📧 Encontradas {len(info_files)} boletas pendientes')
        )
        
        limite = options['limite']
        procesadas = 0
        exitosas = 0
        
        for info_file in info_files[:limite]:
            if procesadas >= limite:
                break
                
            try:
                # Leer información del email
                email_info = self.leer_info_email(info_file)
                
                if not email_info:
                    continue
                
                self.stdout.write(f"\n📋 Procesando boleta #{email_info['equipo_id']}")
                self.stdout.write(f"   📧 Email: {email_info['email']}")
                self.stdout.write(f"   📄 PDF: {email_info['pdf_filename']}")
                
                if options['test']:
                    self.stdout.write("   🧪 Modo prueba - no se enviará")
                    procesadas += 1
                    continue
                
                # Leer PDF
                pdf_path = os.path.join(pending_dir, email_info['pdf_filename'])
                
                if not os.path.exists(pdf_path):
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ PDF no encontrado: {pdf_path}")
                    )
                    continue
                
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                # Intentar reenvío
                subject = f"Boleta de Recepción #{email_info['equipo_id']} - Clínica PC"
                message = f"""
Estimado/a cliente,

Adjunto encontrará la boleta de recepción para su equipo #{email_info['equipo_id']}.

Esta boleta confirma que hemos recibido su equipo y contiene toda la información relevante sobre el estado actual y los siguientes pasos.

Por favor, conserve esta boleta como comprobante de nuestro servicio.

Si tiene alguna pregunta, no dude en contactarnos.

Saludos cordiales,
Equipo Clínica PC
                """.strip()
                
                result = send_email_with_fallback_services(
                    to_email=email_info['email'],
                    subject=subject,
                    message=message,
                    attachment_data=pdf_content,
                    attachment_name=f"boleta_{email_info['equipo_id']}.pdf"
                )
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Reenviada exitosamente con {result['provider']}")
                    )
                    
                    # Mover archivos a carpeta de procesados
                    self.mover_a_procesados(info_file, pdf_path, pending_dir)
                    exitosas += 1
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ Error: {result['message']}")
                    )
                
                procesadas += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Error procesando {info_file}: {str(e)}")
                )
                continue
        
        # Resumen final
        self.stdout.write(f"\n📊 RESUMEN:")
        self.stdout.write(f"   📧 Procesadas: {procesadas}")
        self.stdout.write(f"   ✅ Exitosas: {exitosas}")
        self.stdout.write(f"   ❌ Fallidas: {procesadas - exitosas}")
        
        if exitosas > 0:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 {exitosas} boletas reenviadas exitosamente')
            )

    def leer_info_email(self, info_file):
        """Lee la información del email desde el archivo"""
        try:
            info = {}
            with open(info_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        if key == 'Equipo ID':
                            info['equipo_id'] = value.strip()
                        elif key == 'Email Cliente':
                            info['email'] = value.strip()
                        elif key == 'PDF':
                            info['pdf_filename'] = value.strip()
            
            return info if all(k in info for k in ['equipo_id', 'email', 'pdf_filename']) else None
            
        except Exception as e:
            logger.error(f"Error leyendo {info_file}: {str(e)}")
            return None

    def mover_a_procesados(self, info_file, pdf_file, pending_dir):
        """Mueve archivos procesados a carpeta de completados"""
        try:
            import shutil
            from datetime import datetime
            
            # Crear carpeta de procesados
            processed_dir = os.path.join(pending_dir, 'procesados')
            os.makedirs(processed_dir, exist_ok=True)
            
            # Agregar timestamp a los nombres
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Mover archivos
            base_info = os.path.basename(info_file)
            base_pdf = os.path.basename(pdf_file)
            
            new_info = f"processed_{timestamp}_{base_info}"
            new_pdf = f"processed_{timestamp}_{base_pdf}"
            
            shutil.move(info_file, os.path.join(processed_dir, new_info))
            shutil.move(pdf_file, os.path.join(processed_dir, new_pdf))
            
        except Exception as e:
            logger.error(f"Error moviendo archivos: {str(e)}")
# 🖥️ Clínica PC - Sistema de Gestión Técnica

Sistema completo de gestión para servicios técnicos de computadoras con roles específicos, seguimiento de equipos, diagnósticos y documentación completa.

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/DiegoHenriquez17-lab/clinica_pc.git
cd clinica_pc
```

### 2. Instalar Dependencias
```bash
# Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Instalar paquetes
pip install -r requirements.txt
```

### 3. Configurar Base de Datos (PostgreSQL)
Clona el archivo `.env` de ejemplo y ajústalo:

```bash
copy .env.example .env   # Windows
notepad .env
```

Valores mínimos recomendados para local:

```
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
EMAIL_PROVIDER=console

DB_ENGINE=postgres
DB_NAME=clinica_pc
DB_USER=clinica_user
DB_PASSWORD=Inacap2025
DB_HOST=127.0.0.1
DB_PORT=5432
```

Luego inicializa la base de datos:

```bash
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); u,created=U.objects.get_or_create(username='admin', defaults={'is_superuser':True,'is_staff':True}); u.set_password('Inacap2025'); u.save(); print('ADMIN OK')"
```

### 4. Ejecutar
```bash
python manage.py runserver
```

🎉 **¡Listo!** Visita: http://127.0.0.1:8000/

## 🔑 Credenciales de Acceso

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `Inacap2025` | Administrador completo |
| `recepcion` | `admin123` | Recepción de equipos |
| `diagnostico` | `admin123` | Diagnósticos |
| `tecnico_hardware` | `admin123` | Reparaciones hardware |
| `tecnico_software` | `admin123` | Reparaciones software |
| `despacho` | `admin123` | Entrega de equipos |

## 🎯 Características Principales

### ✅ Sistema de Roles
- **6 tipos de usuarios** con permisos específicos
- **Navegación condicional** según el rol del usuario
- **Protección de vistas** con decoradores personalizados

### ✅ Gestión Completa de Equipos
- **Recepción:** Registro con imagen de carnet del cliente
- **Diagnóstico:** Evaluación técnica y derivación por áreas
- **Reparación:** Separación hardware/software con técnicos especializados
- **Entrega:** Control de despacho y documentación

### ✅ Funcionalidades de Seguridad
- **Imágenes de carnet** de clientes por seguridad
- **Trazabilidad completa** del equipo desde ingreso hasta entrega
- **Historial detallado** de todas las acciones realizadas

### ✅ Documentación Integrada
- **Boletas completas** con toda la información
- **Impresión optimizada** para documentos oficiales
- **Vista de cliente** con historial y estadísticas

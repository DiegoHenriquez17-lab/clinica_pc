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

### 3. Configurar Base de Datos
Antes de migrar, crea un archivo `.env` a partir de `.env.example` y completa las variables para PostgreSQL:

```
DB_ENGINE=postgres
DB_NAME=clinica_pc
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=127.0.0.1
DB_PORT=5432
```
```bash
python manage.py migrate
python manage.py shell -c "exec(open('scripts/operations/setup_roles_complete.py').read())"
```

### 4. Ejecutar
```bash
python manage.py runserver
```

🎉 **¡Listo!** Visita: http://127.0.0.1:8000/

## 🔑 Credenciales de Acceso

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador completo |
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

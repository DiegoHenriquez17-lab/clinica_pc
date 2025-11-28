Link evaluacion2: https://github.com/DiegoHenriquez17-lab/clinica_pc.git
Nombres: Diego Henriquez, Gabriel ruiz

# Guía de Instalación y Ejecución del Proyecto – Clínica PC

## Requisitos previos
• Python 3.12 == https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
• Git
• PostgreSQL / pgAdmin4
• Visual Studio Code (opcional, pero recomendado)

## 1. Clonar el repositorio
Abrir la terminal (CMD) y ejecutar:
```cmd
cd C:\Users\diego\Downloads
git clone https://github.com/DiegoHenriquez17-lab/clinica_pc.git
cd clinica_pc
```

## 2. Crear y activar entorno virtual
Dentro de la carpeta del proyecto, crear el entorno virtual:
```cmd
py -3.12 -m venv venv
venv\Scripts\activate
```
Puedes confirmar con:
```cmd
where python
python -c "import sys; print(sys.executable)"
```

## 3. Instalar dependencias
Instalar las librerías necesarias para el proyecto:
```cmd
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
```
Verificar Django instalado:
```cmd
python -m pip show Django
```

## 🗄️ 4. Configurar PostgreSQL correctamente (Opción A – Recomendado)

Para que Django pueda conectarse a PostgreSQL sin problemas, se debe crear un usuario dedicado y asignarle permisos sobre la base de datos del proyecto.
A continuación, se detallan los pasos que se realizaron en pgAdmin4, junto con su configuración ideal.

### 🔹 1. Crear el usuario del sistema (rol de conexión)

En el panel izquierdo de pgAdmin4, expande tu servidor (por ejemplo, PostgreSQL 18).

Clic derecho sobre Login/Group Roles → Create → Login/Group Role...

En la pestaña General, escribe:

Name: `clinica_user`

En la pestaña Definition, define la contraseña (por ejemplo):

Password: `Inacap2025`

En la pestaña Privileges, deja activado únicamente:

✅ Can login? → Sí

❌ Todo lo demás (Superuser, Create roles, Create databases, etc.)

Clic en Save.

🧠 Esto crea un usuario normal (no superusuario) que puede iniciar sesión, ideal para Django.

### 🔹 2. Crear la base de datos del proyecto

En el panel izquierdo, clic derecho sobre Databases → Create → Database...

En la pestaña General, escribe:

Database name: `clinica_pc`

Owner: `clinica_user` (selecciona el usuario creado en el paso anterior)

Clic en Save.

📘 De esta forma, clinica_user es el dueño total de la base de datos clinica_pc y podrá crear/modificar tablas sin necesidad de permisos extra.

### 🔹 3. Verificar configuración

En Object Explorer → Databases → clinica_pc → Properties, debe aparecer:
Owner: `clinica_user`

En Object Explorer → Login/Group Roles → clinica_user → Privileges, deben estar activadas solo:

✅ Can login?

✅ Inherit rights from the parent roles?

## ⚙️ 5. Configurar archivo .env
Crear el archivo .env en la raíz del proyecto:
```cmd
notepad .env
```

Pegar el siguiente contenido (ajustar contraseña si es necesario):
**Adaptación de cada usuario**

```
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=postgres
DB_NAME=clinica_pc
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=5432
EMAIL_PROVIDER=console

# Servicios de email basados en API (opcional)
# BREVO_API_KEY=tu_api_key_de_brevo
# SENDGRID_API_KEY=tu_api_key_de_sendgrid
```

## 🧩 6. Aplicar migraciones
Ejecutar las migraciones del proyecto:
```cmd
python manage.py migrate
```

Si aparece:
```
No migrations to apply.
```
Significa que todas las migraciones están correctas y la base de datos está lista.

## 👤 7. Crear superusuario
Crear el usuario administrador para ingresar al panel /admin/:
```cmd
python manage.py createsuperuser
```
Ejemplo:
```
Username: admin
Email address: admin@correo.com
Password: Inacap2025
Password (again): Inacap2025
```

## 🚀 8. Ejecutar el servidor
Iniciar el servidor de desarrollo:
```cmd
python manage.py runserver
```

O, si el sistema no reconoce Django (raro, pero seguro):
```cmd
.\venv\Scripts\python manage.py runserver
```

## 9. API REST para Clientes
La carpeta `api/` expone un endpoint REST construido con Django REST Framework.

- Base URL: `http://127.0.0.1:8000/api/`
- Recurso disponible: `clientes`

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| GET | `/api/clientes/` | Lista todos los clientes registrados |
| POST | `/api/clientes/` | Crea un cliente (requiere autenticación) |
| GET | `/api/clientes/{id}/` | Detalle de un cliente |
| PUT/PATCH | `/api/clientes/{id}/` | Actualiza un cliente |
| DELETE | `/api/clientes/{id}/` | Elimina un cliente |

Endpoints disponibles:

- GET `/api/clientes/` — Lista todos los clientes registrados.
- POST `/api/clientes/` — Crea un cliente (requiere autenticación).
- GET `/api/clientes/{id}/` — Devuelve el detalle de un cliente específico.
- PUT/PATCH `/api/clientes/{id}/` — Actualiza los datos de un cliente.
- DELETE `/api/clientes/{id}/` — Elimina un cliente.

Los endpoints usan autenticación estándar de Django (sesión o token). Si accedes desde el navegador estando autenticado en el panel de administración, podrás crear y modificar registros directamente desde la interfaz web que entrega DRF. Para consumirlos desde herramientas externas (Postman, Thunder Client, etc.) asegúrate de enviar las credenciales o tokens correspondientes.

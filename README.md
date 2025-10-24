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

## 🗄️ 4. Crear la base de datos en PostgreSQL
1. Abrir pgAdmin4
2. Clic derecho en Databases → Create → Database
3. Nombre: `clinica_pc`
4. Owner: `postgres`
5. Guardar

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

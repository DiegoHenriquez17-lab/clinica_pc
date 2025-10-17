# 🚀 GUÍA DE INSTALACIÓN - CLÍNICA PC
# =====================================

# 1. CLONAR EL REPOSITORIO
git clone https://github.com/DiegoHenriquez17-lab/clinica_pc.git
cd clinica_pc

# 2. CREAR ENTORNO VIRTUAL (RECOMENDADO)
python -m venv venv

# Activar entorno virtual:
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 3. INSTALAR DEPENDENCIAS
pip install -r requirements.txt

# 4. CONFIGURAR BASE DE DATOS
# El proyecto está configurado para usar Neon (PostgreSQL en la nube).
# Si deseas usar SQLite local, cambia la configuración en gestion_clinica/settings.py
python manage.py migrate

# 5. CONFIGURAR USUARIOS Y ROLES DEL SISTEMA
python manage.py setup_initial_data

# 6. EJECUTAR SERVIDOR
python manage.py runserver

# ✅ LISTO! El proyecto estará en: http://127.0.0.1:8000/

# 🔑 CREDENCIALES:
# Admin: admin / admin123
# Recepción: recepcion / admin123
# Diagnóstico: diagnostico / admin123
# Hardware: tecnico_hardware / admin123
# Software: tecnico_software / admin123
# Despacho: despacho / admin123

# 📱 URLS PRINCIPALES:
# - Inicio: http://127.0.0.1:8000/
# - Dashboard: http://127.0.0.1:8000/dashboard/
# - Recepción: http://127.0.0.1:8000/recepcion/
# - Django Admin: http://127.0.0.1:8000/admin/

# 🗄️ CONFIGURACIÓN DE BASE DE DATOS
# El proyecto usa Neon PostgreSQL. Si necesitas cambiar la configuración,
# edita DATABASES en gestion_clinica/settings.py

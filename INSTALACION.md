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
pip install django==5.2.6
pip install Pillow

# 4. CONFIGURAR BASE DE DATOS
python manage.py migrate

# 5. CREAR SUPERUSUARIO (OPCIONAL)
python manage.py createsuperuser

# 6. CONFIGURAR USUARIOS Y ROLES DEL SISTEMA
python manage.py shell -c "exec(open('setup_roles_complete.py').read())"

# 7. EJECUTAR SERVIDOR
python manage.py runserver

# ✅ LISTO! El proyecto estará en: http://127.0.0.1:8000/

# 🔑 CREDENCIALES:
# Admin: admin / admin123
# Recepción: recepcion / recepcion123  
# Diagnóstico: diagnostico / diagnostico123
# Hardware: hardware / hardware123
# Software: software / software123
# Despacho: despacho / despacho123

# 📱 URLS PRINCIPALES:
# - Inicio: http://127.0.0.1:8000/
# - Dashboard: http://127.0.0.1:8000/dashboard/
# - Recepción: http://127.0.0.1:8000/recepcion/
# - Django Admin: http://127.0.0.1:8000/admin/
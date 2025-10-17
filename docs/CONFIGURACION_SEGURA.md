# 🔐 CONFIGURACIÓN SEGURA DE VARIABLES DE ENTORNO

## ⚠️ PROBLEMA RESUELTO: Ya no más contraseñas hardcodeadas

Antes teníamos las contraseñas directamente en el código, lo cual es una **PÉSIMA práctica de seguridad**. Ahora usamos variables de entorno que:

- ✅ Mantienen las credenciales fuera del código fuente
- ✅ No se suben accidentalmente a GitHub
- ✅ Permiten diferentes configuraciones por ambiente
- ✅ Son fáciles de cambiar sin tocar código

## 📋 CONFIGURACIÓN INICIAL (Solo una vez)

### 1. Crear archivo de variables de entorno

```bash
# Copia el archivo de ejemplo
cp .env.example .env
```

### 2. Configurar Gmail para el envío de emails

1. **Ve a tu cuenta de Gmail** → Gestionar tu cuenta
2. **Seguridad** → Verificación en 2 pasos (debe estar activada)
3. **Contraseñas de aplicación** → Crear nueva
4. **Selecciona "Correo"** y tu dispositivo
5. **Copia la contraseña de 16 caracteres** que aparece

### 3. Editar el archivo .env

```env
# Cambiar por tus valores reales:
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # La contraseña de aplicación de 16 caracteres
```

## 🔄 CAMBIAR CONTRASEÑA EN EL FUTURO

Ahora cuando Gmail expire la contraseña (cada cierto tiempo), simplemente:

1. **Genera nueva contraseña** en Gmail
2. **Edita el archivo .env** (cambiar solo EMAIL_HOST_PASSWORD)
3. **Reinicia el servidor** (`python manage.py runserver`)

**¡YA NO HAY QUE TOCAR CÓDIGO NUNCA MÁS!**

## 🏢 CONFIGURACIÓN POR AMBIENTE

### Desarrollo Local
```env
DEBUG=True
EMAIL_HOST_USER=tu-email-desarrollo@gmail.com
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Producción
```env
DEBUG=False
EMAIL_HOST_USER=clinica.pc.empresa@gmail.com
ALLOWED_HOSTS=clinica-pc.com,www.clinica-pc.com
```

## 📦 INSTALACIÓN EN NUEVO SERVIDOR

```bash
# 1. Clonar repositorio
git clone https://github.com/DiegoHenriquez17-lab/clinica_pc.git

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar configuración
cp .env.example .env

# 4. Editar .env con valores reales
nano .env

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Iniciar servidor
python manage.py runserver
```

## 🔒 SEGURIDAD GARANTIZADA

- ✅ El archivo `.env` está en `.gitignore` (nunca se sube a GitHub)
- ✅ Las credenciales están separadas del código
- ✅ Cada desarrollador puede tener sus propias credenciales
- ✅ Fácil rotación de contraseñas sin cambiar código
- ✅ Configuración diferente por ambiente (dev/prod)

## 🚨 IMPORTANTE

- **NUNCA** subas el archivo `.env` a GitHub
- **SIEMPRE** usa el archivo `.env.example` como plantilla
- **CAMBIA** las contraseñas de aplicación cada 3-6 meses
- **USA** contraseñas de aplicación específicas para cada servidor

---

**¡Ahora el sistema es profesional y seguro! 🎉**
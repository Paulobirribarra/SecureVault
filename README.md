# 🔐 SecureVault - Gestor de Contraseñas

![SecureVault Logo](https://img.shields.io/badge/SecureVault-v1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2.23-green.svg)
![Angular](https://img.shields.io/badge/Angular-20-red.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)

SecureVault es un gestor de contraseñas seguro y moderno, similar a Bitwarden, construido con Django REST Framework y Angular. Ofrece cifrado AES-256 de extremo a extremo y una interfaz de usuario moderna e intuitiva.

## ✨ Características Principales

- 🔐 **Cifrado AES-256** de doble capa para máxima seguridad
- 🔑 **Autenticación JWT** con renovación automática de tokens
- 🌐 **Aplicación web moderna** con Angular y Tailwind CSS
- 📱 **Diseño responsive** optimizado para móviles y escritorio
- 🛡️ **Sistema de seguridad robusto** con rate limiting y validaciones
- 📊 **Análisis de seguridad** automático de contraseñas
- 🔍 **Generador de contraseñas** seguras personalizable
- 📁 **Organización por carpetas** para mejor gestión
- 🔄 **Sincronización en tiempo real** entre dispositivos
- 🚨 **Notificaciones inteligentes** para alertas de seguridad

## 🏗️ Arquitectura

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   FRONTEND      │    (REST API)    │    BACKEND      │
│   Angular 20    │ ←──────────────→ │   Django 4.2    │
│   TypeScript    │                  │   Python 3.11   │
│   Tailwind CSS  │                  │   PostgreSQL    │
└─────────────────┘                  └─────────────────┘
```

**[📖 Ver documentación completa de arquitectura](./documentation/ARQUITECTURA.md)**

## 🚀 Instalación Rápida (Con Scripts)

### ⚡ Opción 1: Automatizada (Recomendada)
```powershell
# 1. Clonar repositorio
git clone https://github.com/Paulobirribarra/SecureVault.git
cd SecureVault

# 2. Configurar proyecto
.\scripts\setup_project.ps1

# 3. Editar backend\.env con tu contraseña de PostgreSQL

# 4. Configurar base de datos
.\scripts\setup_database.ps1

# 5. Ejecutar servidores
.\scripts\run_servers.ps1
```

### 🔧 Opción 2: Manual (Paso a Paso)

### ✅ Prerequisitos

> ⚠️ **IMPORTANTE**: Si tienes múltiples versiones de Python (web + Microsoft Store), revisa la sección de solución de problemas.

- **Python 3.11+** ([Descargar aquí](https://www.python.org/downloads/))
  - ❌ **NO instalar desde Microsoft Store** (causa conflictos)
  - ✅ **Descargar solo desde python.org**
  - ✅ **Marcar "Add to PATH" durante instalación**
- **Node.js 18+** ([Descargar aquí](https://nodejs.org/))
- **PostgreSQL 13+** ([Descargar aquí](https://www.postgresql.org/download/))
- **Git** ([Descargar aquí](https://git-scm.com/downloads))

### 📁 1. Clonar el Repositorio
```bash
git clone https://github.com/Paulobirribarra/SecureVault.git
cd SecureVault
```

### 🗄️ 2. Configurar PostgreSQL
1. **Iniciar PostgreSQL** (asegúrate de que esté ejecutándose)
2. **Crear la base de datos**:
```bash
# Conectar a PostgreSQL como superusuario
psql -U postgres -h localhost -p 5432

# Crear la base de datos (dentro de psql)
CREATE DATABASE secure_app_db;

# Salir de psql
\q
```

### 🐍 3. Configurar Backend (Django)
```bash
# Ir a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
# source venv/bin/activate

# Actualizar pip y herramientas básicas
python -m pip install --upgrade pip
pip install --upgrade setuptools

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Configurar variables de entorno
# Copiar archivo de ejemplo
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac

# IMPORTANTE: Editar el archivo .env con tus credenciales:
# - Cambiar DATABASE_PASSWORD por tu contraseña de PostgreSQL
# - Generar claves secretas únicas para producción
```

### 🔑 4. Configurar Variables de Entorno
Editar el archivo `backend/.env` con tus datos:
```env
# Cambiar esta línea con tu contraseña de PostgreSQL
DATABASE_PASSWORD=tu_contraseña_postgresql

# Para desarrollo puedes dejar el resto como está
# Para producción, genera claves únicas y seguras
```

**🔐 IMPORTANTE - Generar claves seguras para producción:**
```bash
# Generar SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generar clave JWT (32 caracteres mínimo)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generar clave de cifrado AES-256 (32 bytes en base64)
python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### 📊 5. Crear y Aplicar Migraciones
```bash
# Asegúrate de estar en la carpeta backend/ con el entorno virtual activo

# Crear migraciones para las aplicaciones personalizadas
python manage.py makemigrations usuarios
python manage.py makemigrations core

# Aplicar todas las migraciones
python manage.py migrate

# (Opcional) Crear superusuario para el admin
python manage.py createsuperuser
```

### 🚀 6. Iniciar Servidor Backend
```bash
# Desde backend/ con entorno virtual activo
python manage.py runserver

# El backend estará disponible en: http://localhost:8000
```

### 🅰️ 7. Configurar Frontend (Angular)
```bash
# En una NUEVA terminal, ir a la carpeta frontend
cd secure-app-frontend

# Instalar dependencias de Node.js
npm install

# Iniciar servidor de desarrollo
ng serve

# El frontend estará disponible en: http://localhost:4200
```

### 🌐 8. Acceder a la Aplicación
- **🎨 Frontend**: http://localhost:4200
- **🔧 Backend API**: http://localhost:8000/api
- **⚙️ Admin Django**: http://localhost:8000/admin
- **📚 Documentación API**: http://localhost:8000/api/schema/swagger-ui/

### 🔧 Solución de Problemas Comunes

#### ❌ **PROBLEMA CRÍTICO: Múltiples versiones de Python**
Si tienes Python instalado desde la **web oficial** + **Microsoft Store**, esto causa conflictos:

```powershell
# 1. Verificar cuántas versiones tienes
where.exe python

# 2. Si ves múltiples rutas (problemático):
# E:\Paulo\Github\SecureVault\venv\Scripts\python.exe  ← Correcto (venv)
# C:\Users\[usuario]\AppData\Local\Microsoft\WindowsApps\python.exe  ← PROBLEMÁTICO
# C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe  ← Web oficial
```

**💡 Solución:**
```powershell
# Opción A: Desinstalar Python de Microsoft Store
# 1. Ir a Configuración → Apps → buscar "Python"
# 2. Desinstalar versión de Microsoft Store

# Opción B: Usar rutas absolutas en scripts (recomendado)
# Los scripts automáticos ya están configurados para esto
```

#### ❌ Error "ModuleNotFoundError: No module named 'django'"
**Causa:** Entorno virtual no activado correctamente

**Solución:**
```powershell
# 1. Ir al directorio backend
cd backend

# 2. Activar entorno virtual FORZADAMENTE
& "venv\Scripts\Activate.ps1"

# 3. Verificar que esté activo
python -c "import sys; print('Python:', sys.executable)"
# Debe mostrar: Python: E:\Paulo\Github\SecureVault\backend\venv\Scripts\python.exe

# 4. Si no funciona, usar ruta absoluta
& "E:\Paulo\Github\SecureVault\backend\venv\Scripts\python.exe" manage.py runserver
```

#### ❌ Error "ModuleNotFoundError: No module named 'pkg_resources'"
```bash
pip install --upgrade setuptools
```

#### ❌ Error de conexión a PostgreSQL
1. Verificar que PostgreSQL esté ejecutándose
2. Confirmar credenciales en el archivo `.env`
3. Probar conexión: `psql -U postgres -h localhost`

#### ❌ Error de migraciones inconsistentes
```bash
# Limpiar migraciones (solo si es necesario)
# ⚠️ CUIDADO: Esto borra datos existentes
python manage.py migrate --fake-initial
```

#### ❌ Puerto 4200 o 8000 en uso
```bash
# Para Angular (puerto diferente)
ng serve --port 4201

# Para Django (puerto diferente)
python manage.py runserver 8001
```

### 🔄 Proceso de Replicación (Nuevo PC)

1. **Instalar prerequisitos** (Python, Node.js, PostgreSQL, Git)
2. **Clonar repositorio**: `git clone ...`
3. **Configurar PostgreSQL**: Crear base de datos `secure_app_db`
4. **Backend**:
   - Crear entorno virtual
   - Instalar dependencias: `pip install -r requirements.txt`
   - Copiar `.env.example` a `.env` y configurar
   - Ejecutar migraciones: `python manage.py migrate`
   - Iniciar servidor: `python manage.py runserver`
5. **Frontend**:
   - Instalar dependencias: `npm install`
   - Iniciar servidor: `ng serve`

### 📋 Lista de Verificación

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL ejecutándose
- [ ] Base de datos `secure_app_db` creada
- [ ] Entorno virtual Python creado y activado
- [ ] Dependencias instaladas: `pip install -r requirements.txt`
- [ ] Archivo `.env` configurado
- [ ] Migraciones aplicadas: `python manage.py migrate`
- [ ] Servidor backend ejecutándose (puerto 8000)
- [ ] Dependencias frontend instaladas: `npm install`
- [ ] Servidor frontend ejecutándose (puerto 4200)

### ⚠️ Notas de Seguridad

- **🚫 NUNCA** subas el archivo `.env` a Git (ya está en `.gitignore`)
- **🔑 CAMBIA** todas las claves secretas para producción
- **🗄️ USA** variables de entorno en el servidor de producción
- **🔒 CONFIGURA** HTTPS en producción
- **📊 HABILITA** logs de seguridad en producción

## 📁 Estructura del Proyecto

```
SecureVault/
├── 📄 README.md                    # Este archivo
├── 📁 documentation/               # Documentación técnica
│   └── 📄 ARQUITECTURA.md
├── 📁 scripts/                     # Scripts de automatización
│   ├── 📄 README.md               # Guía de scripts
│   ├── 🔧 setup_project.ps1       # Configuración inicial
│   ├── 🗄️ setup_database.ps1      # Configuración de BD
│   ├── 🚀 run_servers.ps1         # Ejecutar servidores
│   └── 🧹 clean_project.ps1       # Limpieza de proyecto
├── 🐍 backend/                     # Backend Django
│   ├── 📁 core/                   # App principal del baúl
│   ├── 📁 usuarios/               # App de autenticación
│   ├── 📁 secure_project/         # Configuración Django
│   ├── 📄 requirements.txt        # Dependencias Python
│   ├── 📄 .env.example           # Ejemplo de configuración
│   └── 📄 manage.py              # CLI Django
├── 🅰️ secure-app-frontend/        # Frontend Angular
│   ├── 📁 src/app/
│   │   ├── 📁 components/        # Componentes reutilizables
│   │   ├── 📁 pages/            # Páginas completas
│   │   ├── 📁 services/         # Servicios HTTP
│   │   ├── 📁 models/           # Tipos TypeScript
│   │   ├── 📁 guards/           # Protección de rutas
│   │   └── 📁 interceptors/     # Middleware HTTP
│   ├── 📄 package.json          # Dependencias npm
│   └── 📄 angular.json          # Configuración Angular
├── 📄 .gitignore                  # Archivos ignorados por Git
└── 📄 secure_app.code-workspace   # Workspace de VS Code
```

## 🛡️ Seguridad

### Características de Seguridad
- **Cifrado AES-256**: Todos los datos sensibles están cifrados
- **Master Password**: Derivación segura con PBKDF2
- **JWT Tokens**: Autenticación stateless con expiración
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Input Validation**: Sanitización en frontend y backend
- **CORS**: Configuración estricta de orígenes
- **CSP Headers**: Content Security Policy

### Buenas Prácticas Implementadas
- ✅ Contraseñas nunca se almacenan en texto plano
- ✅ Tokens JWT con refresh automático
- ✅ Validación de entrada en múltiples capas
- ✅ Logging de actividades de seguridad
- ✅ Headers de seguridad HTTP
- ✅ Protección CSRF activada

## 📱 Capturas de Pantalla

### Login y Registro
![Login Screen](https://via.placeholder.com/800x500?text=Login+Screen)

### Dashboard Principal
![Dashboard](https://via.placeholder.com/800x500?text=Dashboard)

### Gestión de Contraseñas
![Vault Management](https://via.placeholder.com/800x500?text=Vault+Management)

## 🔧 Configuración

### Variables de Entorno (Backend)
```env
# .env file
SECRET_KEY=tu_clave_secreta_django
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/secure_vault
JWT_SECRET_KEY=tu_clave_jwt_secreta
ENCRYPTION_KEY=tu_clave_de_cifrado_aes
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuración Angular
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  appName: 'SecureVault',
  version: '1.0.0'
};
```

## 🔄 API Endpoints

### Autenticación
```http
POST /api/auth/register/     # Registro de usuario
POST /api/auth/login/        # Inicio de sesión
POST /api/auth/logout/       # Cierre de sesión
POST /api/auth/refresh/      # Renovar tokens
GET  /api/auth/user/         # Datos del usuario actual
```

### Gestión del Baúl
```http
GET    /api/vault/items/       # Listar items del baúl
POST   /api/vault/items/       # Crear nuevo item
GET    /api/vault/items/{id}/  # Obtener item específico
PUT    /api/vault/items/{id}/  # Actualizar item
DELETE /api/vault/items/{id}/  # Eliminar item
```

## 🧪 Testing

### Backend (Django)
```bash
cd backend
python manage.py test
```

### Frontend (Angular)
```bash
cd secure-app-frontend
ng test                # Tests unitarios
ng e2e                # Tests de integración
```

## 📚 Documentación Adicional

- 📖 [Arquitectura del Sistema](./documentation/ARQUITECTURA.md)
- 🔧 [Guía de Desarrollo](./documentation/DESARROLLO.md)
- 🚀 [Guía de Despliegue](./documentation/DESPLIEGUE.md)
- 🔐 [Seguridad y Mejores Prácticas](./documentation/SEGURIDAD.md)
- 📡 [Documentación de la API](./documentation/API.md)

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Changelog

### v1.0.0 (2025-06-12)
- ✨ Implementación inicial del sistema de autenticación
- ✨ Dashboard principal con estadísticas de seguridad
- ✨ Sistema de cifrado AES-256 de doble capa
- ✨ Interceptores HTTP y guards de protección
- ✨ UI moderna con Tailwind CSS
- ✨ Sistema de notificaciones en tiempo real

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Paulo** - Desarrollador Full-Stack - [@tu-github](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Inspirado en [Bitwarden](https://bitwarden.com/) por su excelente diseño de seguridad
- [Django REST Framework](https://www.django-rest-framework.org/) por la robusta API
- [Angular](https://angular.io/) por el framework frontend moderno
- [Tailwind CSS](https://tailwindcss.com/) por el sistema de diseño

---

**⭐ Si este proyecto te resulta útil, considera darle una estrella!**

[![GitHub stars](https://img.shields.io/github/stars/tu-usuario/secure-vault.svg?style=social&label=Star)](https://github.com/tu-usuario/secure-vault)

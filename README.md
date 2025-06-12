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

## 🚀 Instalación Rápida

### Prerequisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Paulobirribarra/SecureVault.git
cd secure-vault
```

### 2. Configurar Backend (Django)
```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
# Editar .env con tus credenciales

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### 3. Configurar Frontend (Angular)
```bash
cd secure-app-frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
ng serve
```

### 4. Acceder a la Aplicación
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin

## 📁 Estructura del Proyecto

```
secure-vault/
├── 📄 README.md                    # Este archivo
├── 📁 documentation/               # Documentación técnica
│   └── 📄 ARQUITECTURA.md
├── 🐍 backend/                     # Backend Django
│   ├── 📁 core/                   # App principal del baúl
│   ├── 📁 usuarios/               # App de autenticación
│   ├── 📁 secure_project/         # Configuración Django
│   ├── 📄 requirements.txt        # Dependencias Python
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

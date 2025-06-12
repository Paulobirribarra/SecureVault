# 🏗️ Arquitectura del Sistema SecureVault

## Descripción General

SecureVault es una aplicación web de gestión de contraseñas tipo Bitwarden, construida con una arquitectura moderna full-stack que combina Django REST Framework en el backend y Angular en el frontend.

## 🔧 Stack Tecnológico

### Backend
- **Framework**: Django 4.2.23 + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Cifrado**: AES-256 de doble capa
- **Cache**: Redis (configurado)
- **Servidor**: Gunicorn + Nginx (producción)

### Frontend
- **Framework**: Angular 20
- **UI Framework**: Tailwind CSS
- **Lenguaje**: TypeScript
- **Build Tool**: Angular CLI
- **Testing**: Jasmine + Karma

## 🏛️ Arquitectura General

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│                 │    (REST API)    │                 │
│   FRONTEND      │ ←──────────────→ │    BACKEND      │
│   (Angular)     │                  │    (Django)     │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
         ▲                                     ▲
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│   Browser       │                  │   PostgreSQL    │
│   Storage       │                  │   Database      │
└─────────────────┘                  └─────────────────┘
```

## 📁 Estructura del Proyecto

```
secure_app/
├── backend/                    # Aplicación Django
│   ├── core/                  # App principal del baúl
│   ├── usuarios/              # App de autenticación
│   ├── secure_project/        # Configuración Django
│   ├── requirements.txt       # Dependencias Python
│   └── manage.py             # CLI Django
├── secure-app-frontend/       # Aplicación Angular
│   ├── src/app/
│   │   ├── components/       # Componentes reutilizables
│   │   ├── pages/           # Páginas completas
│   │   ├── services/        # Servicios HTTP
│   │   ├── models/          # Tipos TypeScript
│   │   ├── guards/          # Protección de rutas
│   │   └── interceptors/    # Middleware HTTP
│   ├── package.json         # Dependencias npm
│   └── angular.json         # Configuración Angular
└── documentation/            # Documentación del proyecto
```

## 🔄 Flujo de Datos

### 1. Autenticación
```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as Angular
    participant D as Django
    participant DB as PostgreSQL

    U->>A: Ingresa credenciales
    A->>D: POST /api/auth/login/
    D->>DB: Verifica usuario
    DB->>D: Datos del usuario
    D->>A: JWT tokens
    A->>A: Guarda tokens en localStorage
    A->>U: Redirige a dashboard
```

### 2. Gestión de Contraseñas
```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as Angular
    participant D as Django
    participant C as Crypto
    participant DB as PostgreSQL

    U->>A: Crea nueva contraseña
    A->>D: POST /api/vault/items/
    D->>C: Cifra con AES-256
    C->>D: Datos cifrados
    D->>DB: Guarda en vault_item
    DB->>D: Confirmación
    D->>A: Item creado
    A->>U: Notificación de éxito
```

## 🛡️ Seguridad

### Autenticación y Autorización
- **JWT Tokens**: Access token (5min) + Refresh token (7 días)
- **Interceptores**: Renovación automática de tokens
- **Guards**: Protección de rutas frontend
- **Middleware**: Validación de tokens en backend

### Cifrado de Datos
- **AES-256**: Cifrado simétrico de doble capa
- **Master Password**: Clave derivada del usuario
- **Salt**: Único por usuario para evitar rainbow tables
- **PBKDF2**: Derivación segura de claves

### Medidas Adicionales
- **Rate Limiting**: Prevención de ataques de fuerza bruta
- **CORS**: Configuración estricta de orígenes
- **CSP**: Content Security Policy headers
- **Input Validation**: Sanitización en frontend y backend

## 📡 API REST

### Endpoints de Autenticación
```
POST   /api/auth/register/     # Registro de usuario
POST   /api/auth/login/        # Inicio de sesión
POST   /api/auth/logout/       # Cierre de sesión
POST   /api/auth/refresh/      # Renovar tokens
GET    /api/auth/user/         # Datos del usuario
PUT    /api/auth/user/         # Actualizar perfil
```

### Endpoints del Baúl
```
GET    /api/vault/items/       # Listar items
POST   /api/vault/items/       # Crear item
GET    /api/vault/items/{id}/  # Obtener item
PUT    /api/vault/items/{id}/  # Actualizar item
DELETE /api/vault/items/{id}/  # Eliminar item

GET    /api/vault/folders/     # Listar carpetas
POST   /api/vault/folders/     # Crear carpeta
```

## 🗃️ Modelos de Datos

### Usuario (Django)
```python
class CustomUser(AbstractUser):
    email = EmailField(unique=True)
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    is_email_verified = BooleanField(default=False)
    social_accounts = JSONField(default=dict)
```

### Item del Baúl (Django)
```python
class VaultItem(Model):
    user = ForeignKey(CustomUser)
    name = CharField(max_length=255)
    item_type = CharField(choices=ITEM_TYPES)
    encrypted_data = TextField()
    folder = ForeignKey(VaultFolder, null=True)
    is_favorite = BooleanField(default=False)
```

### Correspondencia TypeScript
```typescript
export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_email_verified: boolean;
}

export interface VaultItem {
    id: string;
    name: string;
    item_type: 'login' | 'note' | 'card' | 'identity';
    is_favorite: boolean;
    created_at: string;
    updated_at: string;
}
```

## 🧩 Componentes Angular

### Estructura de Componentes
```
components/
├── toast/              # Notificaciones
│   ├── toast.ts       # Lógica TypeScript
│   ├── toast.html     # Template HTML
│   └── toast.scss     # Estilos SCSS
└── vault/
    ├── vault-item/
    ├── vault-list/
    └── password-generator/

pages/
├── auth/
│   ├── login/
│   └── register/
└── dashboard/
```

### Servicios
```typescript
AuthService      # Manejo de autenticación
VaultService     # Operaciones del baúl
NotificationService  # Sistema de notificaciones
```

### Guards y Interceptores
```typescript
AuthGuard        # Protege rutas autenticadas
GuestGuard       # Protege rutas de invitados
AuthInterceptor  # Manejo automático de JWT
```

## 🚀 Despliegue

### Desarrollo
```bash
# Backend
cd backend && python manage.py runserver

# Frontend
cd secure-app-frontend && ng serve
```

### Producción
- **Backend**: Docker + Gunicorn + Nginx
- **Frontend**: Build estático servido por Nginx
- **Base de Datos**: PostgreSQL en contenedor
- **SSL**: Let's Encrypt + Certbot

## 📋 Variables de Entorno

### Backend (.env)
```
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=tu_jwt_secret
ENCRYPTION_KEY=tu_encryption_key
```

### Frontend (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

## 🔧 Configuración de Desarrollo

### Prerequisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Git

### Instalación
1. Clonar repositorio
2. Configurar backend Django
3. Configurar frontend Angular
4. Ejecutar migraciones
5. Iniciar servidores de desarrollo

## 📊 Métricas y Monitoreo

### Logging
- **Django**: Configurado con archivos de log rotativos
- **Angular**: Console logging en desarrollo
- **Nginx**: Access y error logs

### Métricas de Seguridad
- Intentos de login fallidos
- Actividad del baúl
- Detección de contraseñas débiles
- Análisis de seguridad automático

---

**Fecha de última actualización**: 12 de junio de 2025
**Versión**: 1.0.0
**Autor**: Paulo - SecureVault Team

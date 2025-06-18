# 🗂️ SecureVault: Guía de Archivos y Estructura

## 📁 Estructura General del Proyecto

```
SecureVault/
├── 📂 backend/                     # Django API Backend
├── 📂 secure-app-frontend/         # Angular Frontend  
├── 📂 documentation/               # Documentación del proyecto
├── 📂 scripts/                     # Scripts PowerShell para automatización
├── 📄 README.md                    # Instrucciones principales
├── 📄 SETUP_GUIDE.md              # Guía de configuración detallada
└── 📄 secure_app.code-workspace   # Configuración workspace VS Code
```

## 🐍 Backend (Django API) - `/backend/`

### Estructura Principal
```
backend/
├── 📂 core/                    # App principal - Gestión de vault/passwords
├── 📂 usuarios/                # App de autenticación y usuarios
├── 📂 secure_project/          # Configuración principal de Django
├── 📂 templates/               # Templates HTML (para Django-allauth)
├── 📂 static/                  # Archivos estáticos
├── 📂 logs/                    # Logs de la aplicación
├── 📄 manage.py               # Script de gestión Django
├── 📄 requirements.txt        # Dependencias Python
└── 📄 .env                    # Variables de entorno
```

### App `core/` - Gestión de Vault
```
core/
├── 📄 __init__.py
├── 📄 admin.py                # Configuración Django Admin
├── 📄 apps.py                 # Configuración de la app
├── 📄 crypto.py               # Funciones de cifrado AES-256
├── 📄 middleware.py           # Middleware personalizado
├── 📄 models.py               # Modelos: Vault, VaultItem, etc.
├── 📄 tests.py                # Tests de la app
├── 📄 urls.py                 # URLs de la API (/api/vault/)
├── 📄 views.py                # ViewSets API REST
└── 📂 migrations/             # Migraciones de base de datos
```

**Archivos clave en `core/`:**

- **`models.py`**: Define los modelos principales
  - `Vault`: Contenedor de contraseñas
  - `VaultItem`: Items individuales (passwords, notes, etc.)
  - Cifrado automático de campos sensibles

- **`crypto.py`**: Cifrado de doble capa
  ```python
  # Funciones principales:
  encrypt_data()    # Cifra datos con AES-256
  decrypt_data()    # Descifra datos
  generate_key()    # Genera claves de cifrado
  ```

- **`views.py`**: API endpoints REST
  ```python
  # ViewSets principales:
  VaultViewSet      # CRUD de vaults
  VaultItemViewSet  # CRUD de items del vault
  ```

### App `usuarios/` - Autenticación
```
usuarios/
├── 📄 __init__.py
├── 📄 adapters.py             # Adaptadores django-allauth (Google OAuth)
├── 📄 admin.py                # Configuración Django Admin
├── 📄 apps.py                 # Configuración de la app
├── 📄 forms.py                # Formularios de usuario
├── 📄 models.py               # Modelo User personalizado + UserSession
├── 📄 serializers.py          # Serializers para API REST
├── 📄 signals.py              # Señales Django (eventos automáticos)
├── 📄 tests.py                # Tests de la app
├── 📄 urls.py                 # URLs de autenticación (/api/auth/)
├── 📄 validators.py           # Validadores personalizados
├── 📄 views.py                # Views API + vistas web para OAuth
├── 📄 web_views.py            # Vistas web adicionales
└── 📂 migrations/             # Migraciones de base de datos
```

**Archivos clave en `usuarios/`:**

- **`models.py`**: 
  - `User`: Usuario personalizado con cifrado de email
  - `UserSession`: Gestión de sesiones múltiples (límite 5 por usuario)

- **`adapters.py`**: Adaptadores para Google OAuth
  ```python
  CustomSocialAccountAdapter    # Vinculación de cuentas Google
  CustomDefaultAccountAdapter  # Redirección al frontend tras login
  ```

- **`views.py`**: APIs de autenticación
  ```python
  # ViewSets y Views principales:
  CustomUserViewSet           # CRUD usuarios
  CustomRegisterView          # Registro
  CustomLoginView            # Login con JWT
  CustomLogoutView           # Logout + limpieza sesiones
  SocialLoginSuccessView     # Callback Google OAuth
  ```

### Configuración `secure_project/`
```
secure_project/
├── 📄 __init__.py
├── 📄 asgi.py                 # Configuración ASGI (async)
├── 📄 settings.py             # Configuración principal Django
├── 📄 urls.py                 # URLs principales del proyecto
└── 📄 wsgi.py                 # Configuración WSGI (sync)
```

**Archivo clave: `settings.py`**
```python
# Configuraciones importantes:
DATABASES          # PostgreSQL
CORS_SETTINGS      # Para Angular frontend
JWT_SETTINGS       # Configuración tokens JWT
SOCIAL_AUTH        # Google OAuth con django-allauth
ENCRYPTION_KEY     # Clave maestra para cifrado
```

### Templates (para Django-allauth)
```
templates/
├── 📂 base/
│   └── base.html              # Template base
├── 📂 auth/
│   ├── login.html             # Login web (fallback)
│   └── register.html          # Registro web (fallback)
└── dashboard.html             # Dashboard web (no usado en SPA)
```

## 🅰️ Frontend (Angular) - `/secure-app-frontend/`

### Estructura Principal
```
secure-app-frontend/
├── 📂 src/                    # Código fuente Angular
├── 📂 public/                 # Archivos públicos (favicon, etc.)
├── 📄 angular.json            # Configuración Angular CLI
├── 📄 package.json            # Dependencias npm
├── 📄 tailwind.config.js      # Configuración Tailwind CSS
├── 📄 tsconfig.json           # Configuración TypeScript
└── 📄 postcss.config.js       # Configuración PostCSS
```

### Código Fuente `/src/`
```
src/
├── 📄 index.html              # HTML principal
├── 📄 main.ts                 # Entry point de Angular
├── 📄 styles.scss             # Estilos globales
└── 📂 app/                    # Aplicación Angular
    ├── 📄 app.ts              # Componente raíz
    ├── 📄 app.html            # Template raíz
    ├── 📄 app.scss            # Estilos raíz
    ├── 📄 app.config.ts       # Configuración de la app
    ├── 📄 app.routes.ts       # Configuración de rutas
    ├── 📂 components/         # Componentes reutilizables
    ├── 📂 pages/              # Páginas/Vistas principales
    ├── 📂 services/           # Servicios (comunicación API)
    ├── 📂 guards/             # Guards de autenticación
    ├── 📂 interceptors/       # Interceptores HTTP
    └── 📂 models/             # Interfaces TypeScript
```

### Páginas Principales `/pages/`
```
pages/
├── 📂 auth/                   # Páginas de autenticación
│   ├── 📂 login/              # Página de login
│   │   ├── login.ts           # Componente login
│   │   └── login.html         # Template login + Google OAuth
│   ├── 📂 register/           # Página de registro
│   └── 📂 social-callback/    # Callback OAuth Google
│       └── social-callback.ts # Procesa tokens JWT del backend
├── 📂 dashboard/              # Dashboard principal
│   ├── dashboard.ts           # Componente dashboard
│   └── dashboard.html         # Template dashboard
└── 📂 vault/                  # Gestión de vault (futuro)
```

**Archivos clave de autenticación:**

- **`login/login.ts`**: Componente de login
  ```typescript
  // Funciones principales:
  onSubmit()           // Login tradicional
  loginWithGoogle()    # Login con Google OAuth
  ```

- **`social-callback/social-callback.ts`**: Procesa callback de Google
  ```typescript
  // Recibe JWT tokens desde URL params
  // Actualiza AuthService con tokens
  // Redirige a dashboard
  ```

### Servicios `/services/`
```
services/
├── 📄 auth.service.ts         # Servicio de autenticación principal
├── 📄 vault.service.ts        # Servicio de gestión de vault
└── 📄 user.service.ts         # Servicio de gestión de usuarios
```

**Archivo clave: `auth.service.ts`**
```typescript
// Funciones principales:
login()              // Login tradicional
logout()             // Logout + limpieza
register()           // Registro de usuario
isAuthenticated()    // Check si está logueado
getAuthHeaders()     // Headers JWT para requests
handleSocialLogin()  // Procesa login social
```

### Guards y Interceptores
```
guards/
└── 📄 auth.guard.ts           # Protege rutas que requieren auth

interceptors/
└── 📄 auth.interceptor.ts     # Añade JWT a requests HTTP automáticamente
```

### Modelos e Interfaces `/models/`
```
models/
├── 📄 user.interface.ts       # Interface de usuario
├── 📄 vault.interface.ts      # Interface de vault
└── 📄 auth.interface.ts       # Interfaces de autenticación
```

## 🔧 Scripts de Automatización - `/scripts/`

```
scripts/
├── 📄 setup_project.ps1       # Setup inicial completo
├── 📄 run_servers_portable.ps1 # Ejecuta backend + frontend
├── 📄 test_portability.ps1    # Simula "PC nuevo"
├── 📄 setup_database.ps1      # Solo configuración BD
├── 📄 clean_project.ps1       # Limpieza de archivos temporales
└── 📄 README.md               # Documentación de scripts
```

**Scripts principales:**

- **`setup_project.ps1`**: Setup completo desde cero
  ```powershell
  # Ejecuta:
  # 1. Configuración entorno Python
  # 2. Instalación dependencias backend
  # 3. Configuración base de datos
  # 4. Migraciones Django
  # 5. Instalación dependencias frontend
  ```

- **`run_servers_portable.ps1`**: Ejecuta aplicación completa
  ```powershell
  # Ejecuta en paralelo:
  # - Django backend (puerto 8000)
  # - Angular frontend (puerto 4200)
  ```

## 📚 Documentación - `/documentation/`

```
documentation/
├── 📄 ARQUITECTURA.md          # Arquitectura general del sistema
├── 📄 DESARROLLO.md            # Guía de desarrollo y setup
├── 📄 OAUTH_GOOGLE.md          # Documentación Google OAuth completa
└── 📄 ANGULAR_DJANGO_CONCEPTS.md # Esta guía que estás leyendo
```

## 🔑 Archivos de Configuración Importantes

### Backend
- **`.env`**: Variables de entorno sensibles
  ```bash
  SECRET_KEY=...
  DATABASE_URL=...
  GOOGLE_OAUTH2_CLIENT_ID=...
  GOOGLE_OAUTH2_CLIENT_SECRET=...
  ENCRYPTION_KEY=...
  ```

- **`requirements.txt`**: Dependencias Python
  ```
  Django==4.2.23
  djangorestframework==3.15.2
  django-allauth==65.0.2
  django-cors-headers==4.6.0
  djangorestframework-simplejwt==5.3.0
  # ... más dependencias
  ```

### Frontend
- **`package.json`**: Dependencias npm
  ```json
  {
    "dependencies": {
      "@angular/core": "^20.0.0",
      "@angular/router": "^20.0.0",
      "@angular/common": "^20.0.0"
    }
  }
  ```

- **`tailwind.config.js`**: Configuración Tailwind CSS
- **`angular.json`**: Configuración Angular CLI

## 🚀 Flujo de Inicio de la Aplicación

### Desarrollo (usando scripts)
1. **Setup inicial**: `.\scripts\setup_project.ps1`
2. **Ejecutar app**: `.\scripts\run_servers_portable.ps1`
3. **Abrir browser**: `http://localhost:4200`

### Manualmente
1. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend**:
   ```bash
   cd secure-app-frontend
   npm install
   ng serve
   ```

## 🔍 Debugging y Logs

### Backend
- **Logs Django**: `/backend/logs/secure_app.log`
- **Console output**: Terminal donde ejecutas `python manage.py runserver`
- **Django Admin**: `http://localhost:8000/admin/`

### Frontend
- **Browser DevTools**: F12 → Console, Network tabs
- **Angular DevTools**: Browser extension
- **Console output**: Terminal donde ejecutas `ng serve`

## 📝 Comandos Útiles de Desarrollo

### Django
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones  
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test
```

### Angular
```bash
# Generar componente
ng generate component pages/nueva-pagina

# Generar servicio
ng generate service services/nuevo-servicio

# Build para producción
ng build --prod

# Ejecutar tests
ng test
```

## 🎯 Puntos Clave para Recordar

1. **Backend = Solo API**: No renderiza HTML, solo devuelve JSON
2. **Frontend = Solo UI**: Consume APIs, maneja interfaz de usuario
3. **Comunicación = HTTP/JSON**: Frontend habla con Backend vía REST API
4. **Autenticación = JWT**: Tokens en lugar de sesiones de servidor
5. **Estado = Frontend**: Angular maneja el estado de la aplicación
6. **Rutas = Dos tipos**: Django URLs para API, Angular routes para páginas

Esta estructura permite escalabilidad, mantenimiento separado del frontend y backend, y la posibilidad de crear múltiples frontends (web, móvil) que consuman la misma API.

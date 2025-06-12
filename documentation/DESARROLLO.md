# 🔧 Guía de Desarrollo - SecureVault

## 🛠️ Configuración del Entorno de Desarrollo

### Prerequisitos
- **Python 3.11+** con pip
- **Node.js 18+** con npm
- **PostgreSQL 13+**
- **Git**
- **VS Code** (recomendado)

### Extensiones Recomendadas para VS Code
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "angular.ng-template",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "ms-python.black-formatter",
    "ms-python.isort"
  ]
}
```

## 🐍 Configuración Backend (Django)

### 1. Entorno Virtual
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

#### PostgreSQL Local
```sql
-- Conectar a PostgreSQL como superusuario
CREATE DATABASE secure_vault;
CREATE USER vault_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE secure_vault TO vault_user;
```

#### Archivo .env
```env
# Configuración de desarrollo
DEBUG=True
SECRET_KEY=django-insecure-tu-clave-de-desarrollo
DATABASE_URL=postgresql://vault_user:tu_password@localhost:5432/secure_vault
JWT_SECRET_KEY=tu-jwt-secret-para-desarrollo
ENCRYPTION_KEY=tu-clave-aes-256-base64
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

### 4. Migraciones y Datos Iniciales
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos de prueba (opcional)
python manage.py loaddata fixtures/test_data.json
```

### 5. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🅰️ Configuración Frontend (Angular)

### 1. Instalación de Dependencias
```bash
cd secure-app-frontend
npm install
```

### 2. Configuración de Entornos

#### environment.development.ts
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  appName: 'SecureVault Dev',
  version: '1.0.0-dev',
  enableLogging: true
};
```

#### environment.production.ts
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-dominio.com/api',
  appName: 'SecureVault',
  version: '1.0.0',
  enableLogging: false
};
```

### 3. Ejecutar Servidor de Desarrollo
```bash
ng serve --host 0.0.0.0 --port 4200
```

## 📁 Estructura de Desarrollo

### Backend Django
```
backend/
├── core/                       # App principal del baúl
│   ├── models.py              # Modelos de datos cifrados
│   ├── views.py               # API views para vault
│   ├── serializers.py         # Serializadores DRF
│   ├── crypto.py              # Sistema de cifrado
│   └── middleware.py          # Middlewares personalizados
├── usuarios/                   # App de autenticación
│   ├── models.py              # Usuario personalizado
│   ├── views.py               # Auth API views
│   ├── serializers.py         # Serializadores de auth
│   └── validators.py          # Validadores personalizados
└── secure_project/            # Configuración Django
    ├── settings.py            # Configuración principal
    ├── urls.py                # URLs principales
    └── wsgi.py                # WSGI config
```

### Frontend Angular
```
src/app/
├── components/                 # Componentes reutilizables
│   ├── toast/                 # Sistema de notificaciones
│   ├── vault/                 # Componentes del baúl
│   └── shared/                # Componentes compartidos
├── pages/                     # Páginas completas
│   ├── auth/                  # Login/Register
│   ├── dashboard/             # Panel principal
│   └── vault/                 # Gestión del baúl
├── services/                  # Servicios Angular
│   ├── auth.service.ts        # Autenticación
│   ├── vault.service.ts       # Operaciones del baúl
│   └── notification.service.ts # Notificaciones
├── models/                    # Interfaces TypeScript
│   ├── user.model.ts          # Modelos de usuario
│   └── vault.model.ts         # Modelos del baúl
├── guards/                    # Guards de ruta
│   ├── auth.guard.ts          # Protege rutas autenticadas
│   └── guest.guard.ts         # Protege rutas de invitados
└── interceptors/              # Interceptores HTTP
    └── auth.interceptor.ts    # Manejo automático de JWT
```

## 🔧 Comandos de Desarrollo

### Django
```bash
# Crear nueva aplicación
python manage.py startapp nombre_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test

# Colectar archivos estáticos
python manage.py collectstatic

# Crear superusuario
python manage.py createsuperuser
```

### Angular
```bash
# Generar componente
ng generate component nombre-componente

# Generar servicio
ng generate service nombre-servicio

# Generar guard
ng generate guard nombre-guard

# Generar interceptor
ng generate interceptor nombre-interceptor

# Build de producción
ng build --prod

# Ejecutar tests
ng test

# Ejecutar e2e tests
ng e2e

# Analizar bundle
ng build --stats-json
npx webpack-bundle-analyzer dist/stats.json
```

## 🐛 Debugging

### Backend Django
```python
# settings.py - Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Frontend Angular
```typescript
// Habilitar logging en desarrollo
if (!environment.production) {
  console.log('Modo desarrollo activado');
  // Habilitar Angular DevTools
  import('./debug').then(module => module.enableDebugTools());
}
```

## 🧪 Testing

### Tests Backend
```python
# usuarios/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

class UserModelTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')

class AuthAPITest(APITestCase):
    def test_login(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
```

### Tests Frontend
```typescript
// auth.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(AuthService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should login user', () => {
    const loginData = { email: 'test@example.com', password: 'test123' };
    service.login(loginData).subscribe(response => {
      expect(response.access).toBeDefined();
    });
  });
});
```

## 🔄 Workflow de Desarrollo

### 1. Crear Nueva Feature
```bash
# Crear rama de feature
git checkout -b feature/nueva-funcionalidad

# Desarrollo...
# Commits...

# Push y crear PR
git push origin feature/nueva-funcionalidad
```

### 2. Sincronización de Modelos
Cuando cambies modelos en Django, asegúrate de:
1. Actualizar modelos TypeScript correspondientes
2. Actualizar serializers
3. Crear migraciones
4. Actualizar tests

### 3. Convenciones de Código

#### Python (Django)
```python
# PEP 8 compliance
# Usar Black formatter
# Usar isort para imports

# Ejemplo de vista
class VaultItemViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de items del baúl."""
    
    queryset = VaultItem.objects.all()
    serializer_class = VaultItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar items por usuario autenticado."""
        return self.queryset.filter(user=self.request.user)
```

#### TypeScript (Angular)
```typescript
// Usar interfaces para tipos
// Nombrado camelCase para variables
// Nombrado PascalCase para clases/interfaces

// Ejemplo de servicio
@Injectable({
  providedIn: 'root'
})
export class VaultService {
  private readonly apiUrl = `${environment.apiUrl}/vault`;
  
  constructor(private http: HttpClient) {}
  
  getVaultItems(): Observable<VaultItem[]> {
    return this.http.get<VaultItem[]>(`${this.apiUrl}/items/`);
  }
}
```

## 📊 Herramientas de Desarrollo

### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Configuración Git
```bash
# Ignorar archivos específicos del entorno
git config core.excludesfile ~/.gitignore_global

# Configurar usuario
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"
```

## 🚨 Troubleshooting

### Problemas Comunes

#### CORS Issues
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CORS_ALLOW_CREDENTIALS = True
```

#### JWT Token Issues
```typescript
// Verificar en el navegador
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')

// Limpiar tokens si hay problemas
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
```

#### Database Connection
```bash
# Verificar conexión PostgreSQL
psql -h localhost -U vault_user -d secure_vault

# Reiniciar servicios si es necesario
sudo systemctl restart postgresql
```

---

¿Tienes alguna pregunta específica sobre el desarrollo? ¡Estoy aquí para ayudar! 🚀

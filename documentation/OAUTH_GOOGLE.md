# Autenticación OAuth con Google - SecureVault

> **Guía completa del sistema de autenticación social implementado en SecureVault**
> 
> Este documento explica cómo funciona la integración entre Django REST + Angular + Google OAuth

---

## 📖 Índice

1. [Resumen del Sistema](#resumen-del-sistema)
2. [Arquitectura General](#arquitectura-general)
3. [Flujo Completo Paso a Paso](#flujo-completo-paso-a-paso)
4. [Archivos Involucrados](#archivos-involucrados)
5. [Configuración Requerida](#configuración-requerida)
6. [Características de Seguridad](#características-de-seguridad)
7. [Gestión de Sesiones](#gestión-de-sesiones)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Resumen del Sistema

**SecureVault** implementa un sistema híbrido de autenticación que permite:

- ✅ **Login tradicional** con email/password
- ✅ **Login social** con Google OAuth 2.0
- ✅ **Sin duplicación de cuentas** - mismo email funciona para ambos métodos
- ✅ **JWT tokens** para autenticación stateless
- ✅ **Gestión avanzada de sesiones** con límites y expiración

### Diferencias con Django tradicional (Templates)

| Django Tradicional | SecureVault (REST + SPA) |
|-------------------|---------------------------|
| Session-based auth | JWT token-based auth |
| Server-side templates | Client-side Angular |
| django.contrib.auth | django-rest-framework + JWT |
| Cookies automáticas | LocalStorage manual |
| Redirects del servidor | Redirects del cliente |

---

## 🏗️ Arquitectura General

```
┌─────────────────────────┐    ┌──────────────────────────┐    ┌─────────────────────────┐
│     Frontend            │    │       Backend            │    │      Google OAuth       │
│     (Angular)           │    │      (Django REST)       │    │                         │
│                         │    │                          │    │                         │
│  ┌─────────────────┐    │    │  ┌─────────────────────┐ │    │  ┌─────────────────┐   │
│  │ Login Component │────┼────┼─►│ django-allauth      │─┼────┼─►│ Authorization   │   │
│  └─────────────────┘    │    │  └─────────────────────┘ │    │  │ Server          │   │
│                         │    │                          │    │  └─────────────────┘   │
│  ┌─────────────────┐    │    │  ┌─────────────────────┐ │    │           │             │
│  │ Callback Comp.  │◄───┼────┼──│ SocialLoginRedirect │◄┼────┼───────────┘             │
│  └─────────────────┘    │    │  │ View (JWT Generator)│ │    │                         │
│                         │    │  └─────────────────────┘ │    │                         │
│  ┌─────────────────┐    │    │                          │    │                         │
│  │ Auth Service    │    │    │  ┌─────────────────────┐ │    │                         │
│  │ (JWT Storage)   │    │    │  │ Custom Adapters     │ │    │                         │
│  └─────────────────┘    │    │  │ (Account Linking)   │ │    │                         │
│                         │    │  └─────────────────────┘ │    │                         │
└─────────────────────────┘    └──────────────────────────┘    └─────────────────────────┘
```

---

## 🔄 Flujo Completo Paso a Paso

### **Paso 1: Inicialización desde Frontend**

**Usuario hace click en "Continuar con Google"**

📁 `src/app/pages/auth/login/login.html` (líneas 118-130)
```html
<button
  type="button"
  (click)="loginWithGoogle()"
  class="w-full bg-white border border-gray-300..."
>
  <svg><!-- Icono de Google --></svg>
  Continuar con Google
</button>
```

📁 `src/app/pages/auth/login/login.ts` (línea 67)
```typescript
loginWithGoogle(): void {
  this.authService.loginWithGoogle();
}
```

📁 `src/app/services/auth.service.ts` (líneas 142-145)
```typescript
loginWithGoogle(): void {
  // Redirigir directamente a Django-allauth para Google OAuth
  window.location.href = `http://localhost:8000/accounts/google/login/`;
}
```

### **Paso 2: Procesamiento en Backend Django**

**Django-allauth toma el control**

📁 `backend/secure_project/urls.py` (línea 57)
```python
path('accounts/', include('allauth.urls')),
# Esto expone /accounts/google/login/ automáticamente
```

📁 `backend/secure_project/settings.py` (configuración OAuth)
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APPS': [
            {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'settings': {
                    'scope': ['profile', 'email'],
                    'auth_params': {'access_type': 'online'},
                }
            }
        ]
    }
}
```

### **Paso 3: Redirección a Google**

**Django construye la URL de autorización y redirige**

```
https://accounts.google.com/oauth/authorize?
  client_id=TU_CLIENT_ID&
  redirect_uri=http://localhost:8000/accounts/google/login/callback/&
  scope=profile+email&
  response_type=code&
  state=RANDOM_STATE
```

### **Paso 4: Autorización del Usuario**

**Usuario autoriza en Google → Google redirige de vuelta**

```
http://localhost:8000/accounts/google/login/callback/?
  state=RANDOM_STATE&
  code=AUTHORIZATION_CODE&
  scope=profile+email
```

### **Paso 5: Verificación y Vinculación de Cuenta**

**django-allauth ejecuta nuestros adaptadores personalizados**

📁 `backend/usuarios/adapters.py`
```python
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        ANTES de crear/vincular cuenta:
        - Verificar si ya existe usuario con mismo email
        - Vincular cuenta social a cuenta existente
        - Marcar como cuenta social
        """
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            try:
                existing_user = CustomUser.objects.get(email=email)
                sociallogin.user = existing_user
                
                if not existing_user.is_social_account:
                    existing_user.is_social_account = True
                    existing_user.social_provider = sociallogin.account.provider
                    existing_user.email_verified = True
                    existing_user.save()
                    
            except CustomUser.DoesNotExist:
                pass  # Se creará nuevo usuario
    
    def save_user(self, request, sociallogin, form=None):
        """
        Al crear NUEVO usuario social:
        - Marcar como cuenta social
        - Configurar campos específicos
        - Obtener nombre/apellido de Google
        """
        user = sociallogin.user
        user.set_unusable_password()  # No password para cuentas sociales
        user.is_social_account = True
        user.social_provider = sociallogin.account.provider
        user.email_verified = True
        user.is_active = True
        
        # Datos adicionales de Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        
        user.save()
        return user
```

### **Paso 6: Generación de JWT y Redirección**

**Nuestra vista personalizada genera tokens JWT**

📁 `backend/usuarios/views.py` (SocialLoginRedirectView)
```python
class SocialLoginRedirectView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                # Generar tokens JWT para el usuario autenticado
                refresh = RefreshToken.for_user(request.user)
                access_token = refresh.access_token
                
                # Crear/actualizar sesión de usuario
                self.create_user_session(request, request.user)
                
                # Construir URL con tokens para el callback social
                callback_url = f"http://localhost:4200/auth/social-callback?access_token={str(access_token)}&refresh_token={str(refresh)}"
                
                return redirect(callback_url)
```

### **Paso 7: Procesamiento de Tokens en Frontend**

**Componente especializado procesa los tokens**

📁 `src/app/pages/auth/social-callback/social-callback.ts`
```typescript
export class SocialCallback implements OnInit {
  private processSocialLoginTokens(): void {
    this.route.queryParams.subscribe(params => {
      const accessToken = params['access_token'];
      const refreshToken = params['refresh_token'];
      const error = params['error'];

      if (error) {
        this.handleLoginError(error);
        return;
      }

      if (accessToken && refreshToken) {
        // Usar el método handleSocialLogin del AuthService
        this.authService.handleSocialLogin(accessToken, refreshToken).subscribe({
          next: (user) => {
            this.notificationService.success('¡Bienvenido!', 'Has iniciado sesión con Google correctamente');
            this.router.navigate(['/dashboard'], { replaceUrl: true });
          },
          error: (error) => {
            this.notificationService.error('Error', 'No se pudo completar el login social');
            this.router.navigate(['/auth/login'], { replaceUrl: true });
          }
        });
      }
    });
  }
}
```

### **Paso 8: Actualización del Estado de Autenticación**

**AuthService actualiza el estado global**

📁 `src/app/services/auth.service.ts`
```typescript
handleSocialLogin(accessToken: string, refreshToken: string): Observable<User> {
  // 1. Guardar tokens en localStorage
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  
  // 2. Actualizar estado de autenticación
  this.isAuthenticatedSubject.next(true);
  
  // 3. Cargar información del usuario
  return this.getCurrentUser().pipe(
    tap(user => {
      // Usuario cargado → this.currentUserSubject.next(user)
      // Configurar auto-refresh de tokens
    })
  );
}
```

### **Paso 9: Protección de Rutas**

**AuthGuard permite acceso al dashboard**

📁 `src/app/guards/auth.guard.ts`
```typescript
canActivate(): Observable<boolean> {
  return this.authService.isAuthenticated$.pipe(
    take(1),
    map((isAuthenticated: boolean) => {
      if (isAuthenticated) {
        return true;  // ✅ Permitir acceso
      } else {
        this.router.navigate(['/auth/login']);
        return false;
      }
    })
  );
}
```

---

## 📁 Archivos Involucrados

### **Backend (Django REST)**

| Archivo | Propósito | Líneas clave |
|---------|-----------|--------------|
| `backend/.env` | Credenciales OAuth | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| `backend/secure_project/settings.py` | Configuración django-allauth | 187-217 |
| `backend/secure_project/urls.py` | URLs OAuth | 57 |
| `backend/usuarios/adapters.py` | Lógica personalizada OAuth | Todo el archivo |
| `backend/usuarios/views.py` | Vista redirección + JWT | 614-667 |
| `backend/usuarios/models.py` | Modelo usuario + sesiones | 69-408 |
| `backend/usuarios/urls.py` | URL callback social | 38 |

### **Frontend (Angular)**

| Archivo | Propósito | Líneas clave |
|---------|-----------|--------------|
| `src/app/pages/auth/login/login.html` | Botón Google | 118-130 |
| `src/app/pages/auth/login/login.ts` | Acción login Google | 67 |
| `src/app/pages/auth/social-callback/social-callback.ts` | Procesamiento tokens | Todo el archivo |
| `src/app/services/auth.service.ts` | Gestión autenticación | 142-175 |
| `src/app/guards/auth.guard.ts` | Protección rutas | Todo el archivo |
| `src/app/app.routes.ts` | Configuración rutas | 25-27 |

---

## ⚙️ Configuración Requerida

### **1. Google Cloud Console**

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar Google+ API
3. Crear credenciales OAuth 2.0:
   - **Tipo**: Aplicación web
   - **Orígenes autorizados**: `http://localhost:8000`
   - **URIs de redirección**: `http://localhost:8000/accounts/google/login/callback/`

### **2. Variables de Entorno**

📁 `backend/.env`
```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
```

### **3. Configuración Django**

📁 `backend/secure_project/settings.py`
```python
INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

# Configuración django-allauth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
LOGIN_REDIRECT_URL = '/api/v1/usuarios/auth/social-redirect/'

# Adaptadores personalizados
SOCIALACCOUNT_ADAPTER = 'usuarios.adapters.SocialAccountAdapter'
ACCOUNT_ADAPTER = 'usuarios.adapters.AccountAdapter'
```

### **4. Configuración Angular**

📁 `src/app/app.routes.ts`
```typescript
{
  path: 'auth/social-callback',
  loadComponent: () => import('./pages/auth/social-callback/social-callback').then(c => c.SocialCallback)
},
```

---

## 🔐 Características de Seguridad

### **Prevención de Duplicación de Cuentas**
- ✅ **Mismo email**: Funciona para login normal y social
- ✅ **Vinculación automática**: Cuenta existente se marca como social
- ✅ **Sin conflictos**: `pre_social_login()` maneja la vinculación

### **Autenticación JWT**
- ✅ **Stateless**: No depende de sesiones del servidor
- ✅ **Renovación automática**: Refresh tokens
- ✅ **Expiración**: Access tokens expiran (configurable)

### **Protección CSRF**
- ✅ **No requerido**: JWT tokens no son vulnerables a CSRF
- ✅ **SameSite cookies**: Para sesiones de django-allauth

### **Validación de Tokens**
- ✅ **Verificación automática**: JWT incluye verificación de firma
- ✅ **Expiración**: Tokens expiran automáticamente
- ✅ **Invalidación**: Refresh tokens se pueden blacklistear

---

## 📊 Gestión de Sesiones

### **Modelo de Sesión**

📁 `backend/usuarios/models.py`
```python
class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
```

### **Políticas de Sesión**

| Característica | Valor | Justificación |
|----------------|--------|---------------|
| **Duración** | 24 horas | Balance seguridad/UX |
| **Máximo por usuario** | 5 sesiones | Prevenir abuso |
| **Auto-limpieza** | Sí | Sesiones expiradas se desactivan |
| **Información guardada** | IP, User-Agent, Timestamps | Auditoría y seguridad |

### **Flujo de Limpieza**

```python
# En cada login:
1. Terminar sesiones expiradas
2. Si > 5 sesiones activas → terminar las más antiguas
3. Crear/actualizar sesión actual
4. Configurar expiración en 24h
```

---

## 🐛 Troubleshooting

### **Problema: "Login social no redirige al dashboard"**

**Síntomas**: Usuario se autentica pero vuelve al login

**Solución**:
1. Verificar que `isAuthenticatedSubject.next(true)` se ejecute
2. Verificar que tokens se guarden en localStorage
3. Verificar que `AuthGuard` use `isAuthenticated$` observable

### **Problema: "Múltiples sesiones en admin"**

**Síntomas**: Demasiadas sesiones por usuario

**Solución**:
- Es **normal** tener 2-5 sesiones (diferentes navegadores/dispositivos)
- Sistema auto-limpia sesiones expiradas
- Límite de 5 sesiones activas implementado

### **Problema: "Error 500 en callback de Google"**

**Síntomas**: Error después de autorizar en Google

**Soluciones posibles**:
1. Verificar `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`
2. Verificar URI de redirección en Google Console
3. Verificar que adaptadores estén configurados correctamente

### **Problema: "Logout no redirige"**

**Síntomas**: Mensaje de logout pero no va al login

**Solución**: Verificar que logout maneje Observable correctamente:

```typescript
logout(): void {
  this.authService.logout().subscribe({
    next: () => {
      this.notificationService.success('Sesión cerrada', 'Has cerrado sesión correctamente');
      this.router.navigate(['/auth/login']);
    }
  });
}
```

---

## 📈 Comparación: Django Templates vs REST + SPA

| Aspecto | Django Templates | SecureVault (REST+Angular) |
|---------|------------------|----------------------------|
| **Autenticación** | `request.user` automático | JWT tokens manuales |
| **Estado** | Sesiones del servidor | Estado del cliente |
| **Redirecciones** | `redirect()` del servidor | `router.navigate()` del cliente |
| **OAuth** | Redirección directa | Callback + tokens + redirección |
| **Seguridad** | CSRF tokens | JWT signatures |
| **Escalabilidad** | Limitada (sesiones) | Alta (stateless) |
| **Complejidad** | Baja | Media-Alta |
| **Flexibilidad** | Baja | Alta |

---

## 🎯 Próximos Pasos

1. **Implementar refresh automático** de tokens antes de expiración
2. **Agregar más proveedores** OAuth (Facebook, GitHub, etc.)
3. **Implementar 2FA** para cuentas sociales
4. **Dashboard de sesiones** para que usuarios vean/terminen sesiones
5. **Logs de auditoría** para accesos y cambios de cuenta

---

## 🔗 Referencias

- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [JWT.io](https://jwt.io/) - Para entender JWT tokens
- [Angular Guards](https://angular.io/guide/router#preventing-unauthorized-access)

---

> **💡 Consejo**: Este sistema es más complejo que Django tradicional, pero ofrece mayor flexibilidad y escalabilidad. La curva de aprendizaje vale la pena para aplicaciones modernas.

---

*Documentación generada para SecureVault - Sistema de autenticación híbrido Django REST + Angular*

"""
URL configuration for secure_project project.

API REST pura para usar con frontend Angular.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Vista de bienvenida para la API
@csrf_exempt
def api_root(request):
    """Vista raíz de la API con información básica."""
    return JsonResponse({
        'message': 'Secure App - API REST Backend',
        'version': '1.0.0',
        'frontend': 'Angular (puerto 4200)',
        'backend': 'Django REST API (puerto 8000)',
        'endpoints': {
            'authentication': '/api/v1/usuarios/auth/',
            'vault': '/api/v1/core/vault/',
            'documentation': '/api/docs/',
            'admin': '/admin/',
        },
        'features': [
            'Autenticación JWT segura',
            'Verificación de email',
            'Autenticación de dos factores (2FA)',
            'Baúl de contraseñas cifrado AES-256',
            'Gestión de sesiones',
            'OAuth con Google',
            'Rate limiting y seguridad avanzada',
        ]
    })

urlpatterns = [
    # Administración Django (solo para desarrollo)
    path("admin/", admin.site.urls),
    
    # API raíz - información básica
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root-v2'),
    
    # APIs principales para Angular
    path('api/v1/usuarios/', include('usuarios.urls')),
    path('api/v1/core/', include('core.urls')),
    
    # Django Allauth (OAuth) - solo endpoints API
    path('accounts/', include('allauth.urls')),
    
    # Documentación de la API (opcional)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check para el frontend
    path('health/', lambda request: JsonResponse({'status': 'ok', 'backend': 'django'}), name='health-check'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar en desarrollo
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Manejadores de errores personalizados
handler404 = lambda request, exception: JsonResponse({
    'error': 'Endpoint no encontrado',
    'status_code': 404
}, status=404)

handler500 = lambda request: JsonResponse({
    'error': 'Error interno del servidor',
    'status_code': 500
}, status=500)

"""
Middleware personalizado para seguridad y headers adicionales.
Implementa headers de seguridad y prevención de ataques comunes.
"""

import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import re

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware que agrega headers de seguridad adicionales.
    Implementa protecciones contra XSS, CSRF, clickjacking, etc.
    """
    
    def process_response(self, request, response):
        """Agrega headers de seguridad a todas las respuestas."""
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://apis.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # Headers adicionales de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Header personalizado para identificar la API
        response['X-Secure-App'] = 'v1.0'
        
        # Cache control para recursos sensibles
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware personalizado de rate limiting por IP.
    Complementa django-ratelimit con controles adicionales.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Verifica rate limits antes de procesar la request."""
        
        # Obtener IP del cliente
        ip_address = self.get_client_ip(request)
        
        # Rate limit para login attempts
        if request.path.startswith('/api/v1/auth/login/'):
            return self.check_login_rate_limit(request, ip_address)
        
        # Rate limit para registro
        if request.path.startswith('/api/v1/auth/register/'):
            return self.check_register_rate_limit(request, ip_address)
        
        # Rate limit general para API
        if request.path.startswith('/api/'):
            return self.check_api_rate_limit(request, ip_address)
        
        return None
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    def check_login_rate_limit(self, request, ip_address):
        """Rate limit específico para intentos de login."""
        if request.method != 'POST':
            return None
        
        cache_key = f'login_attempts:{ip_address}'
        attempts = cache.get(cache_key, 0)
        
        # Máximo 5 intentos por IP en 15 minutos
        if attempts >= 5:
            logger.warning(f'Login rate limit exceeded for IP: {ip_address}')
            return HttpResponseForbidden(
                'Demasiados intentos de login. Intenta más tarde.'
            )
        
        # Incrementar contador
        cache.set(cache_key, attempts + 1, 15 * 60)  # 15 minutos
        return None
    
    def check_register_rate_limit(self, request, ip_address):
        """Rate limit para registro de nuevos usuarios."""
        if request.method != 'POST':
            return None
        
        cache_key = f'register_attempts:{ip_address}'
        attempts = cache.get(cache_key, 0)
        
        # Máximo 3 registros por IP por hora
        if attempts >= 3:
            logger.warning(f'Registration rate limit exceeded for IP: {ip_address}')
            return HttpResponseForbidden(
                'Demasiados registros desde esta IP. Intenta más tarde.'
            )
        
        cache.set(cache_key, attempts + 1, 60 * 60)  # 1 hora
        return None
    
    def check_api_rate_limit(self, request, ip_address):
        """Rate limit general para la API."""
        cache_key = f'api_requests:{ip_address}'
        requests = cache.get(cache_key, 0)
        
        # Máximo 1000 requests por IP por hora
        if requests >= 1000:
            logger.warning(f'API rate limit exceeded for IP: {ip_address}')
            return HttpResponseForbidden('Rate limit exceeded')
        
        cache.set(cache_key, requests + 1, 60 * 60)  # 1 hora
        return None


class UserAgentValidationMiddleware(MiddlewareMixin):
    """
    Middleware que valida User-Agent para prevenir bots maliciosos.
    """
    
    # User agents sospechosos/bloqueados
    BLOCKED_USER_AGENTS = [
        r'.*bot.*',
        r'.*crawler.*',
        r'.*spider.*',
        r'.*scraper.*',
        r'.*wget.*',
        r'.*curl.*',
    ]
    
    # Endpoints que requieren User-Agent válido
    PROTECTED_PATHS = [
        r'^/api/v1/auth/',
        r'^/admin/',
    ]
    
    def process_request(self, request):
        """Valida el User-Agent en rutas protegidas."""
        
        # Verificar si la ruta requiere validación
        if not any(re.match(pattern, request.path) for pattern in self.PROTECTED_PATHS):
            return None
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Bloquear User-Agents vacíos en rutas sensibles
        if not user_agent:
            logger.warning(f'Empty User-Agent blocked from {self.get_client_ip(request)}')
            return HttpResponseForbidden('Invalid request')
        
        # Verificar User-Agents bloqueados
        for pattern in self.BLOCKED_USER_AGENTS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                logger.warning(f'Blocked User-Agent: {user_agent} from {self.get_client_ip(request)}')
                return HttpResponseForbidden('Access denied')
        
        return None
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


class CSRFTokenMiddleware(MiddlewareMixin):
    """
    Middleware personalizado para validación adicional de CSRF.
    """
    
    def process_request(self, request):
        """Validaciones adicionales de CSRF para API."""
        
        # Solo aplicar a requests POST/PUT/DELETE de la API
        if (request.method in ['POST', 'PUT', 'DELETE'] and 
            request.path.startswith('/api/')):
            
            # Verificar header Referer para requests de API
            referer = request.META.get('HTTP_REFERER', '')
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            
            if referer and not any(referer.startswith(origin) for origin in allowed_origins):
                logger.warning(f'Invalid referer for API request: {referer}')
                # No bloquear automáticamente, solo loggear
        
        return None


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware para gestionar timeout de sesiones automáticamente.
    """
    
    def process_request(self, request):
        """Verifica timeout de sesión."""
        
        if request.user.is_authenticated:
            # Verificar última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                timeout_duration = timedelta(hours=1)  # 1 hora de timeout
                
                if timezone.now() - last_activity_time > timeout_duration:
                    # Sesión expirada
                    request.session.flush()
                    logger.info(f'Session timeout for user: {request.user.email}')
                    return None
            
            # Actualizar última actividad
            request.session['last_activity'] = timezone.now().isoformat()
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging de requests importantes.
    """
    
    # Rutas que requieren logging especial
    LOGGED_PATHS = [
        r'^/api/v1/auth/',
        r'^/admin/',
    ]
    
    def process_request(self, request):
        """Loggea requests importantes."""
        
        if any(re.match(pattern, request.path) for pattern in self.LOGGED_PATHS):
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]
            
            logger.info(
                f'Request: {request.method} {request.path} '
                f'from {ip_address} '
                f'User-Agent: {user_agent}'
            )
        
        return None
    
    def process_response(self, request, response):
        """Loggea respuestas de requests importantes."""
        
        if any(re.match(pattern, request.path) for pattern in self.LOGGED_PATHS):
            ip_address = self.get_client_ip(request)
            
            logger.info(
                f'Response: {response.status_code} for {request.method} {request.path} '
                f'from {ip_address}'
            )
        
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

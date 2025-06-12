"""
Signals para el modelo de usuario.
Gestiona la creación automática de perfiles y otras acciones relacionadas.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.utils import timezone
from django.contrib.sessions.models import Session
from .models import CustomUser, UserProfile, UserSession
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un nuevo usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f'Perfil creado para usuario: {instance.email}')


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Maneja acciones cuando un usuario inicia sesión exitosamente.
    """
    # Resetear intentos fallidos
    user.reset_failed_login()
    
    # Actualizar último acceso
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Crear registro de sesión
    if hasattr(request, 'session'):
        # Obtener información de la request
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Crear o actualizar sesión
        session, created = UserSession.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={
                'user': user,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': timezone.now() + timezone.timedelta(hours=24),
            }
        )
        
        if not created:
            session.last_activity = timezone.now()
            session.is_active = True
            session.save(update_fields=['last_activity', 'is_active'])
    
    logger.info(f'Usuario {user.email} inició sesión desde {ip_address}')


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    Maneja intentos de login fallidos.
    """
    email = credentials.get('username') or credentials.get('email')
    
    if email:
        try:
            user = CustomUser.objects.get(email=email)
            user.increment_failed_login()
            
            ip_address = get_client_ip(request)
            logger.warning(
                f'Intento de login fallido para {email} desde {ip_address}. '
                f'Intentos fallidos: {user.failed_login_attempts}'
            )
            
            # Si la cuenta se bloquea, registrar evento de seguridad
            if user.is_account_locked():
                logger.error(f'Cuenta {email} bloqueada debido a múltiples intentos fallidos')
                
        except CustomUser.DoesNotExist:
            # Log de intento con email inexistente
            ip_address = get_client_ip(request)
            logger.warning(f'Intento de login con email inexistente: {email} desde {ip_address}')


@receiver(post_delete, sender=Session)
def session_deleted_handler(sender, instance, **kwargs):
    """
    Limpia las sesiones de usuario cuando se elimina una sesión de Django.
    """
    try:
        user_session = UserSession.objects.get(session_key=instance.session_key)
        user_session.terminate()
        logger.info(f'Sesión terminada: {instance.session_key}')
    except UserSession.DoesNotExist:
        pass


def get_client_ip(request):
    """
    Obtiene la dirección IP real del cliente.
    Considera proxies y load balancers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def cleanup_expired_sessions():
    """
    Función para limpiar sesiones expiradas.
    Debe ser llamada por un task periódico (celery, cron, etc.)
    """
    expired_count = UserSession.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    ).update(is_active=False)
    
    logger.info(f'Limpiadas {expired_count} sesiones expiradas')
    return expired_count

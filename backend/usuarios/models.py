"""
Modelos de usuario personalizados para el sistema de autenticación segura.
Incluye validaciones robustas, perfiles de usuario y gestión de sesiones.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .validators import validate_full_name, validate_phone_number


class CustomUserManager(BaseUserManager):
    """Manager personalizado para el modelo de usuario."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario regular."""
        if not email:
            raise ValueError(_('El email es obligatorio'))
        
        email = self.normalize_email(email)
        
        # Verificar si el email ya existe (incluyendo cuentas sociales)
        if self.model.objects.filter(email=email).exists():
            raise ValidationError(_('Ya existe una cuenta con este email.'))
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('El superusuario debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('El superusuario debe tener is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    
    def get_or_create_social_user(self, email, **extra_fields):
        """
        Obtiene o crea un usuario para autenticación social.
        Previene duplicados de email entre cuentas normales y sociales.
        """
        try:
            # Buscar usuario existente por email
            user = self.get(email=email)
              # Si existe pero no es cuenta social, actualizar campos sociales
            if not user.is_social_account:
                user.is_social_account = True
                user.email_verified = True  # Las cuentas sociales vienen verificadas
                user.save()
            
            return user, False
        except self.model.DoesNotExist:
            # Crear nuevo usuario social
            extra_fields.setdefault('is_social_account', True)
            extra_fields.setdefault('email_verified', True)
            extra_fields.setdefault('is_active', True)
            # IMPORTANTE: Asegurar que NO tenga permisos de admin por defecto
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            
            user = self.model(email=email, **extra_fields)
            user.save(using=self._db)
            return user, True


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado que usa email como identificador único.
    
    Características:
    - Email único como username
    - Validación de contraseña robusta
    - Verificación de email obligatoria
    - Soporte para cuentas sociales
    - Prevención de duplicados entre cuentas normales y sociales
    """
    
    # Campos básicos
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _('email'),
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este email.'),
        },
        help_text=_('Dirección de email única para identificar al usuario.')
    )
    
    # Información personal
    first_name = models.CharField(
        _('nombre'),
        max_length=150,
        validators=[validate_full_name],
        help_text=_('Nombre del usuario (máximo 150 caracteres).')
    )
    last_name = models.CharField(
        _('apellido'),
        max_length=150,
        blank=True,
        validators=[validate_full_name],
        help_text=_('Apellido del usuario (opcional, máximo 150 caracteres).')
    )
    
    # Estados de la cuenta
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Designa si este usuario debe ser tratado como activo. '
                   'Desmarca esto en lugar de eliminar cuentas.')
    )
    is_staff = models.BooleanField(
        _('staff'),
        default=False,
        help_text=_('Designa si el usuario puede acceder al sitio de administración.')
    )
    
    # Verificación de email
    email_verified = models.BooleanField(
        _('email verificado'),
        default=False,
        help_text=_('Indica si el email ha sido verificado.')
    )
    email_verification_token = models.CharField(
        _('token de verificación'),
        max_length=64,
        blank=True,
        null=True,
        help_text=_('Token para verificación de email.')
    )
    
    # Cuentas sociales
    is_social_account = models.BooleanField(
        _('cuenta social'),
        default=False,
        help_text=_('Indica si la cuenta fue creada mediante autenticación social.')
    )
    social_provider = models.CharField(
        _('proveedor social'),
        max_length=50,
        blank=True,
        choices=[
            ('google', 'Google'),
            ('facebook', 'Facebook'),
            ('github', 'GitHub'),
        ],
        help_text=_('Proveedor de autenticación social utilizado.')
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('fecha de registro'), default=timezone.now)
    last_login = models.DateTimeField(_('último acceso'), blank=True, null=True)
    password_changed_at = models.DateTimeField(
        _('contraseña cambiada'),
        auto_now_add=True,
        help_text=_('Fecha y hora del último cambio de contraseña.')
    )
    
    # Seguridad adicional
    failed_login_attempts = models.PositiveIntegerField(
        _('intentos fallidos'),
        default=0,
        help_text=_('Número de intentos de login fallidos consecutivos.')
    )
    account_locked_until = models.DateTimeField(
        _('cuenta bloqueada hasta'),
        blank=True,
        null=True,
        help_text=_('Fecha hasta la cual la cuenta está bloqueada.')
    )
    
    # Configuración del manager
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    
    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['email_verified']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    def clean(self):
        """Validaciones adicionales del modelo."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name or self.email.split('@')[0]
    
    def get_username(self):
        """Retorna el username del usuario para compatibilidad con django-allauth."""
        return self.email
    
    @property
    def username(self):
        """Propiedad username para compatibilidad con django-allauth."""
        return self.email
    
    @username.setter
    def username(self, value):
        """Setter para username - asigna el valor al email."""
        self.email = value
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Envía un email al usuario."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada."""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Bloquea la cuenta por un tiempo determinado."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Desbloquea la cuenta."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def increment_failed_login(self):
        """Incrementa el contador de intentos fallidos."""
        self.failed_login_attempts += 1
        
        # Bloquear cuenta después de 5 intentos fallidos
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login(self):
        """Reinicia el contador de intentos fallidos."""
        if self.failed_login_attempts > 0:
            self.failed_login_attempts = 0
            self.save(update_fields=['failed_login_attempts'])


class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información adicional.
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('usuario')
    )
    
    # Información adicional
    phone_number = models.CharField(
        _('teléfono'),
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
        help_text=_('Número de teléfono del usuario.')
    )
    birth_date = models.DateField(
        _('fecha de nacimiento'),
        blank=True,
        null=True,
        help_text=_('Fecha de nacimiento del usuario.')
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Imagen de perfil del usuario.')
    )
    
    # Configuraciones de privacidad
    is_profile_public = models.BooleanField(
        _('perfil público'),
        default=False,
        help_text=_('Determina si el perfil es visible públicamente.')
    )
    
    # Configuraciones de seguridad
    two_factor_enabled = models.BooleanField(
        _('2FA habilitado'),
        default=False,
        help_text=_('Indica si la autenticación de dos factores está habilitada.')
    )
    two_factor_secret = models.CharField(
        _('secreto 2FA'),
        max_length=32,
        blank=True,
        help_text=_('Secreto para autenticación de dos factores.')
    )
    
    # Metadatos
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('Perfil de Usuario')
        verbose_name_plural = _('Perfiles de Usuario')
    
    def __str__(self):
        return f'Perfil de {self.user.get_full_name()}'
    
    def get_age(self):
        """Calcula la edad del usuario."""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class UserSession(models.Model):
    """
    Modelo para trackear sesiones de usuario activas.
    Permite gestión avanzada de sesiones y seguridad.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('usuario')
    )
    session_key = models.CharField(
        _('clave de sesión'),
        max_length=40,
        unique=True,
        help_text=_('Identificador único de la sesión.')
    )
    ip_address = models.GenericIPAddressField(
        _('dirección IP'),
        help_text=_('Dirección IP desde la cual se inició la sesión.')
    )
    user_agent = models.TextField(
        _('user agent'),
        help_text=_('Información del navegador/dispositivo.')
    )
    location = models.CharField(
        _('ubicación'),
        max_length=200,
        blank=True,
        help_text=_('Ubicación geográfica aproximada.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('creada'), auto_now_add=True)
    last_activity = models.DateTimeField(_('última actividad'), auto_now=True)
    expires_at = models.DateTimeField(
        _('expira'),
        help_text=_('Fecha y hora de expiración de la sesión.')
    )
    
    # Estado
    is_active = models.BooleanField(_('activa'), default=True)
    
    class Meta:
        verbose_name = _('Sesión de Usuario')
        verbose_name_plural = _('Sesiones de Usuario')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f'Sesión de {self.user.email} - {self.ip_address}'
    
    def is_expired(self):
        """Verifica si la sesión ha expirado."""
        return timezone.now() > self.expires_at
    
    def extend_session(self, hours=24):
        """Extiende la duración de la sesión."""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])
    
    def terminate(self):
        """Termina la sesión."""
        self.is_active = False
        self.save(update_fields=['is_active'])

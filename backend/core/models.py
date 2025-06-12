"""
Modelos para el sistema de baúl de contraseñas cifrado.
Implementa almacenamiento seguro de datos sensibles similar a Bitwarden.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .crypto import VaultEntry, AESCrypto
import json
import logging

logger = logging.getLogger(__name__)


class VaultFolder(models.Model):
    """
    Carpetas para organizar las entradas del baúl.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_folders',
        verbose_name=_('usuario')
    )
    name = models.CharField(
        _('nombre'),
        max_length=100,
        help_text=_('Nombre de la carpeta (máximo 100 caracteres)')
    )
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#007bff',
        help_text=_('Color hex para la carpeta (ej: #007bff)')
    )
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('Carpeta del Baúl')
        verbose_name_plural = _('Carpetas del Baúl')
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f'{self.user.email} - {self.name}'


class VaultItem(models.Model):
    """
    Entrada individual en el baúl de contraseñas.
    Todos los datos sensibles se almacenan cifrados.
    """
    
    ITEM_TYPES = [
        ('login', _('Credenciales de Login')),
        ('note', _('Nota Segura')),
        ('card', _('Tarjeta de Crédito')),
        ('identity', _('Información Personal')),
        ('file', _('Archivo Seguro')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_items',
        verbose_name=_('usuario')
    )
    folder = models.ForeignKey(
        VaultFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        verbose_name=_('carpeta')
    )
    
    # Metadatos no cifrados
    item_type = models.CharField(
        _('tipo de entrada'),
        max_length=20,
        choices=ITEM_TYPES,
        default='login'
    )
    name = models.CharField(
        _('nombre'),
        max_length=200,
        help_text=_('Nombre descriptivo de la entrada')
    )
    is_favorite = models.BooleanField(
        _('favorito'),
        default=False,
        help_text=_('Marcar como favorito para acceso rápido')
    )
    
    # Datos cifrados
    encrypted_data = models.JSONField(
        _('datos cifrados'),
        help_text=_('Datos sensibles cifrados con AES-256')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    last_accessed = models.DateTimeField(
        _('último acceso'),
        null=True,
        blank=True,
        help_text=_('Última vez que se accedió a esta entrada')
    )
    
    # Metadatos de seguridad
    access_count = models.PositiveIntegerField(
        _('contador de accesos'),
        default=0,
        help_text=_('Número de veces que se ha accedido a esta entrada')
    )
    
    class Meta:
        verbose_name = _('Entrada del Baúl')
        verbose_name_plural = _('Entradas del Baúl')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'item_type']),
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', 'folder']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.get_item_type_display()})'
    
    def save_encrypted_data(self, data: dict, user_password: str):
        """
        Guarda datos cifrados en la entrada.
        
        Args:
            data (dict): Datos a cifrar y guardar
            user_password (str): Contraseña maestra del usuario
        """
        try:
            vault = VaultEntry()
            
            # Preparar datos con metadatos
            entry_data = {
                'type': self.item_type,
                'name': self.name,
                'favorite': self.is_favorite,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': timezone.now().isoformat(),
                **data
            }
            
            # Cifrar y guardar
            self.encrypted_data = vault.create_entry(user_password, entry_data)
            
            logger.info(f'Encrypted data saved for vault item: {self.name}')
            
        except Exception as e:
            logger.error(f'Error saving encrypted data: {str(e)}')
            raise ValidationError(f'Error al cifrar datos: {str(e)}')
    
    def get_decrypted_data(self, user_password: str) -> dict:
        """
        Obtiene los datos descifrados de la entrada.
        
        Args:
            user_password (str): Contraseña maestra del usuario
        
        Returns:
            dict: Datos descifrados
        """
        try:
            vault = VaultEntry()
            decrypted_data = vault.decrypt_entry(self.encrypted_data, user_password)
            
            # Actualizar estadísticas de acceso
            self.access_count += 1
            self.last_accessed = timezone.now()
            self.save(update_fields=['access_count', 'last_accessed'])
            
            logger.info(f'Vault item accessed: {self.name}')
            return decrypted_data
            
        except Exception as e:
            logger.error(f'Error decrypting data: {str(e)}')
            raise ValidationError(f'Error al descifrar datos: {str(e)}')
    
    def update_encrypted_data(self, updates: dict, user_password: str):
        """
        Actualiza datos cifrados existentes.
        
        Args:
            updates (dict): Datos a actualizar
            user_password (str): Contraseña maestra del usuario
        """
        try:
            vault = VaultEntry()
            self.encrypted_data = vault.update_entry(
                self.encrypted_data, 
                user_password, 
                updates
            )
            
            logger.info(f'Vault item updated: {self.name}')
            
        except Exception as e:
            logger.error(f'Error updating encrypted data: {str(e)}')
            raise ValidationError(f'Error al actualizar datos: {str(e)}')
    
    def get_safe_preview(self) -> dict:
        """
        Retorna una vista previa segura sin datos sensibles.
        
        Returns:
            dict: Datos seguros para mostrar en listas
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.item_type,
            'type_display': self.get_item_type_display(),
            'is_favorite': self.is_favorite,
            'folder': self.folder.name if self.folder else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count
        }


class VaultItemShare(models.Model):
    """
    Modelo para compartir entradas del baúl con otros usuarios.
    Los datos se cifran con claves específicas para cada usuario.
    """
    
    PERMISSION_CHOICES = [
        ('read', _('Solo Lectura')),
        ('write', _('Lectura y Escritura')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vault_item = models.ForeignKey(
        VaultItem,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name=_('entrada del baúl')
    )
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_shares_given',
        verbose_name=_('compartido por')
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_shares_received',
        verbose_name=_('compartido con')
    )
    permission = models.CharField(
        _('permisos'),
        max_length=10,
        choices=PERMISSION_CHOICES,
        default='read'
    )
    
    # Datos cifrados específicos para el usuario receptor
    encrypted_data_for_user = models.JSONField(
        _('datos cifrados para usuario'),
        help_text=_('Datos cifrados con la clave del usuario receptor')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    expires_at = models.DateTimeField(
        _('expira'),
        null=True,
        blank=True,
        help_text=_('Fecha de expiración del compartir (opcional)')
    )
    is_active = models.BooleanField(_('activo'), default=True)
    
    class Meta:
        verbose_name = _('Compartir Entrada del Baúl')
        verbose_name_plural = _('Compartir Entradas del Baúl')
        unique_together = ['vault_item', 'shared_with']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.vault_item.name} compartido con {self.shared_with.email}'
    
    def is_expired(self):
        """Verifica si el compartir ha expirado."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class VaultActivity(models.Model):
    """
    Log de actividades en el baúl para auditoría.
    """
    
    ACTION_CHOICES = [
        ('create', _('Crear')),
        ('read', _('Leer')),
        ('update', _('Actualizar')),
        ('delete', _('Eliminar')),
        ('share', _('Compartir')),
        ('unshare', _('Dejar de Compartir')),
        ('export', _('Exportar')),
        ('import', _('Importar')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vault_activities',
        verbose_name=_('usuario')
    )
    vault_item = models.ForeignKey(
        VaultItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        verbose_name=_('entrada del baúl')
    )
    action = models.CharField(
        _('acción'),
        max_length=20,
        choices=ACTION_CHOICES
    )
    description = models.TextField(
        _('descripción'),
        blank=True,
        help_text=_('Descripción detallada de la actividad')
    )
    ip_address = models.GenericIPAddressField(
        _('dirección IP'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True
    )
    timestamp = models.DateTimeField(_('fecha y hora'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Actividad del Baúl')
        verbose_name_plural = _('Actividades del Baúl')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['vault_item', 'action']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        item_name = self.vault_item.name if self.vault_item else 'Item eliminado'
        return f'{self.user.email} - {self.get_action_display()} - {item_name}'


class MasterPasswordHash(models.Model):
    """
    Almacena el hash de la contraseña maestra del usuario.
    Se usa para verificar la contraseña sin almacenarla en texto plano.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='master_password',
        verbose_name=_('usuario')
    )
    password_hash = models.CharField(
        _('hash de contraseña'),
        max_length=128,
        help_text=_('Hash de la contraseña maestra')
    )
    salt = models.CharField(
        _('salt'),
        max_length=32,
        help_text=_('Salt usado para el hash')
    )
    iterations = models.PositiveIntegerField(
        _('iteraciones'),
        default=100000,
        help_text=_('Número de iteraciones PBKDF2')
    )
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('Hash de Contraseña Maestra')
        verbose_name_plural = _('Hashes de Contraseñas Maestras')
    
    def __str__(self):
        return f'Contraseña maestra de {self.user.email}'
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada coincide con la almacenada.
        
        Args:
            password (str): Contraseña a verificar
        
        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            crypto = AESCrypto()
            derived_key, _ = crypto.generate_key_from_password(
                password, 
                bytes.fromhex(self.salt)
            )
            
            # Comparar hashes
            import hashlib
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                bytes.fromhex(self.salt),
                self.iterations
            )
            
            stored_hash = bytes.fromhex(self.password_hash)
            return hashlib.compare_digest(password_hash, stored_hash)
            
        except Exception as e:
            logger.error(f'Error verifying master password: {str(e)}')
            return False
    
    def set_password(self, password: str):
        """
        Establece una nueva contraseña maestra.
        
        Args:
            password (str): Nueva contraseña maestra
        """
        try:
            import hashlib
            import secrets
            
            # Generar salt aleatorio
            salt = secrets.token_hex(16)
            
            # Generar hash
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                bytes.fromhex(salt),
                self.iterations
            )
            
            self.salt = salt
            self.password_hash = password_hash.hex()
            
            logger.info(f'Master password set for user: {self.user.email}')
            
        except Exception as e:
            logger.error(f'Error setting master password: {str(e)}')
            raise ValidationError(f'Error al establecer contraseña maestra: {str(e)}')

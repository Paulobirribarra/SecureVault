"""
Validadores personalizados para el modelo de usuario.
Implementa validaciones de seguridad para contraseñas robustas.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Validador personalizado para contraseñas robustas.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 número
    - Al menos 1 símbolo especial
    """
    
    def __init__(self, min_length=8):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        errors = []
        
        # Verificar longitud mínima
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    _('La contraseña debe tener al menos %(min_length)d caracteres.'),
                    code='password_too_short',
                    params={'min_length': self.min_length},
                )
            )
        
        # Verificar al menos una mayúscula
        if not re.search(r'[A-Z]', password):
            errors.append(
                ValidationError(
                    _('La contraseña debe contener al menos una letra mayúscula.'),
                    code='password_no_uppercase',
                )
            )
        
        # Verificar al menos un número
        if not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    _('La contraseña debe contener al menos un número.'),
                    code='password_no_number',
                )
            )
        
        # Verificar al menos un símbolo especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(
                ValidationError(
                    _('La contraseña debe contener al menos un símbolo especial (!@#$%^&*(),.?":{}|<>).'),
                    code='password_no_symbol',
                )
            )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            'Tu contraseña debe tener al menos %(min_length)d caracteres, '
            'incluyendo al menos una mayúscula, un número y un símbolo especial.'
        ) % {'min_length': self.min_length}


def validate_full_name(value):
    """Validador para nombre completo."""
    if not value or len(value.strip()) < 2:
        raise ValidationError(
            _('El nombre debe tener al menos 2 caracteres.'),
            code='name_too_short'
        )
    
    # Solo letras, espacios y algunos caracteres especiales
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', value):
        raise ValidationError(
            _('El nombre solo puede contener letras, espacios, guiones y apostrofes.'),
            code='invalid_name_characters'
        )


def validate_phone_number(value):
    """Validador para número de teléfono."""
    if value:
        # Formato básico para teléfonos internacionales
        phone_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_pattern, value.replace(' ', '').replace('-', '')):
            raise ValidationError(
                _('Ingrese un número de teléfono válido.'),
                code='invalid_phone'
            )

"""
Formularios personalizados para el modelo de usuario.
Incluye validaciones de seguridad y creación/edición de usuarios.
"""

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class UserCreationForm(forms.ModelForm):
    """
    Formulario para crear nuevos usuarios en el admin.
    Incluye validación de contraseñas robustas.
    """
    
    password1 = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una contraseña segura'
        }),
        help_text=_(
            'La contraseña debe tener al menos 8 caracteres, '
            'incluir mayúsculas, números y símbolos especiales.'
        )
    )
    password2 = forms.CharField(
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña'
        }),
        help_text=_('Ingrese la misma contraseña para verificación.')
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario@ejemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
        }
    
    def clean_password2(self):
        """Valida que las contraseñas coincidan."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Las contraseñas no coinciden.'))
        
        return password2
    
    def clean_email(self):
        """Valida que el email sea único."""
        email = self.cleaned_data.get('email')
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError(_('Ya existe un usuario con este email.'))
        return email
    
    def save(self, commit=True):
        """Guarda el usuario con la contraseña hasheada."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Formulario para editar usuarios existentes en el admin.
    """
    
    password = ReadOnlyPasswordHashField(
        label=_('Contraseña'),
        help_text=_(
            'Las contraseñas no se almacenan en texto plano, por lo que no hay '
            'forma de ver la contraseña de este usuario, pero puedes cambiarla '
            'usando <a href="{}">este formulario</a>.'
        )
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'email', 'password', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'email_verified', 'is_social_account', 'social_provider'
        )
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualizar el enlace de cambio de contraseña
        if self.instance.pk:
            password_change_url = f'../../{self.instance.pk}/password/'
            self.fields['password'].help_text = self.fields['password'].help_text.format(
                password_change_url
            )


class UserRegistrationForm(forms.ModelForm):
    """
    Formulario de registro público para nuevos usuarios.
    """
    
    password1 = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña segura',
            'required': True
        }),
        help_text=_(
            'Mínimo 8 caracteres con mayúsculas, números y símbolos.'
        )
    )
    password2 = forms.CharField(
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'required': True
        })
    )
    terms_accepted = forms.BooleanField(
        label=_('Acepto los términos y condiciones'),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
        }
    
    def clean_password2(self):
        """Valida que las contraseñas coincidan."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Las contraseñas no coinciden.'))
        
        return password2
    
    def clean_email(self):
        """Valida que el email sea único."""
        email = self.cleaned_data.get('email')
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError(
                    _('Ya existe una cuenta con este email. '
                      '¿Quizás quieras iniciar sesión?')
                )
        return email
    
    def save(self, commit=True):
        """Crea el usuario con email sin verificar."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True  # Activar, pero email sin verificar
        user.email_verified = False
        
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Formulario de inicio de sesión.
    """
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'required': True,
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña',
            'required': True
        })
    )
    remember_me = forms.BooleanField(
        label=_('Recordarme'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        """Validación general del formulario."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                
                # Verificar si la cuenta está bloqueada
                if user.is_account_locked():
                    raise ValidationError(
                        _('Tu cuenta está temporalmente bloqueada debido a múltiples '
                          'intentos fallidos. Intenta más tarde.')
                    )
                
                # Verificar si el usuario está activo
                if not user.is_active:
                    raise ValidationError(_('Esta cuenta está desactivada.'))
                
            except CustomUser.DoesNotExist:
                pass  # No revelar si el email existe o no
        
        return cleaned_data


class PasswordResetForm(forms.Form):
    """
    Formulario para solicitar restablecimiento de contraseña.
    """
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'required': True
        }),
        help_text=_(
            'Ingresa tu email y te enviaremos un enlace para '
            'restablecer tu contraseña.'
        )
    )


class PasswordResetConfirmForm(forms.Form):
    """
    Formulario para confirmar nueva contraseña.
    """
    
    password1 = forms.CharField(
        label=_('Nueva contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña segura',
            'required': True
        }),
        help_text=_(
            'Mínimo 8 caracteres con mayúsculas, números y símbolos.'
        )
    )
    password2 = forms.CharField(
        label=_('Confirmar nueva contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña',
            'required': True
        })
    )
    
    def clean_password2(self):
        """Valida que las contraseñas coincidan."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Las contraseñas no coinciden.'))
        
        return password2

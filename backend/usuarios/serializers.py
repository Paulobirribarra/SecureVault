"""
Serializers para la API REST del sistema de usuarios.
Maneja serialización y validación de datos para las vistas API.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser, UserProfile, UserSession


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información básica del usuario."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    is_account_locked = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'short_name',
            'is_active', 'email_verified', 'is_social_account', 'social_provider',
            'date_joined', 'last_login', 'failed_login_attempts', 'is_account_locked'
        ]
        read_only_fields = [
            'id', 'email', 'is_active', 'email_verified', 'is_social_account',
            'social_provider', 'date_joined', 'last_login', 'failed_login_attempts'
        ]
    
    def get_is_account_locked(self, obj):
        """Retorna si la cuenta está bloqueada."""
        return obj.is_account_locked()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil extendido del usuario."""
    
    user = UserSerializer(read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'phone_number', 'birth_date', 'avatar', 'age',
            'is_profile_public', 'two_factor_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'two_factor_secret']
    
    def get_age(self, obj):
        """Calcula la edad del usuario."""
        return obj.get_age()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    terms_accepted = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'terms_accepted'
        ]
    
    def validate_email(self, value):
        """Valida que el email sea único."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con este email."
            )
        return value
    
    def validate_terms_accepted(self, value):
        """Valida que se hayan aceptado los términos."""
        if not value:
            raise serializers.ValidationError(
                "Debes aceptar los términos y condiciones."
            )
        return value
    
    def validate(self, attrs):
        """Validación de datos del formulario."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crea un nuevo usuario."""
        # Remover campos que no van al modelo
        validated_data.pop('password_confirm')
        validated_data.pop('terms_accepted')
        
        # Crear usuario
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para autenticación de usuarios."""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    remember_me = serializers.BooleanField(default=False)
    totp_code = serializers.CharField(max_length=6, required=False)
    
    def validate(self, attrs):
        """Validación de credenciales."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Verificar que el usuario existe
            try:
                user = CustomUser.objects.get(email=email)
                
                # Verificar si la cuenta está bloqueada
                if user.is_account_locked():
                    raise serializers.ValidationError(
                        'Tu cuenta está temporalmente bloqueada debido a múltiples '
                        'intentos fallidos. Intenta más tarde.'
                    )
                
                # Verificar si el usuario está activo
                if not user.is_active:
                    raise serializers.ValidationError('Esta cuenta está desactivada.')
                
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError('Credenciales inválidas.')
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validación del cambio de contraseña."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden.'
            })
        
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer para solicitud de restablecimiento de contraseña."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Valida que el email exista en el sistema."""
        if not CustomUser.objects.filter(email=value).exists():
            # No revelar si el email existe o no por seguridad
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar restablecimiento de contraseña."""
    
    token = serializers.CharField()
    email = serializers.EmailField()
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validación del restablecimiento de contraseña."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden.'
            })
        
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de usuario."""
    
    is_current = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    location_display = serializers.CharField(source='location', read_only=True)
    device_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_key', 'ip_address', 'user_agent', 'location_display',
            'device_info', 'created_at', 'last_activity', 'expires_at',
            'is_active', 'is_current', 'is_expired'
        ]
        read_only_fields = [
            'session_key', 'ip_address', 'user_agent', 'created_at',
            'last_activity', 'expires_at'
        ]
    
    def get_is_current(self, obj):
        """Determina si es la sesión actual."""
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False
    
    def get_is_expired(self, obj):
        """Verifica si la sesión ha expirado."""
        return obj.is_expired()
    
    def get_device_info(self, obj):
        """Extrae información del dispositivo del user agent."""
        try:
            user_agent = obj.user_agent.lower()
            
            # Detectar sistema operativo
            if 'windows' in user_agent:
                os = 'Windows'
            elif 'mac' in user_agent:
                os = 'macOS'
            elif 'linux' in user_agent:
                os = 'Linux'
            elif 'android' in user_agent:
                os = 'Android'
            elif 'iphone' in user_agent or 'ipad' in user_agent:
                os = 'iOS'
            else:
                os = 'Desconocido'
            
            # Detectar navegador
            if 'chrome' in user_agent and 'edge' not in user_agent:
                browser = 'Chrome'
            elif 'firefox' in user_agent:
                browser = 'Firefox'
            elif 'safari' in user_agent and 'chrome' not in user_agent:
                browser = 'Safari'
            elif 'edge' in user_agent:
                browser = 'Edge'
            else:
                browser = 'Desconocido'
            
            return f'{browser} en {os}'
            
        except Exception:
            return 'Información no disponible'


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer para actualizar información del perfil."""
    
    # Campos del usuario
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    # Campos del perfil
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    is_profile_public = serializers.BooleanField(default=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'phone_number', 'birth_date',
            'is_profile_public'
        ]
    
    def update(self, instance, validated_data):
        """Actualiza tanto el usuario como el perfil."""
        # Extraer campos del usuario
        user_fields = {
            'first_name': validated_data.pop('first_name', None),
            'last_name': validated_data.pop('last_name', None)
        }
        
        # Actualizar usuario
        user = instance.user
        for field, value in user_fields.items():
            if value is not None:
                setattr(user, field, value)
        user.save()
        
        # Actualizar perfil
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        return instance


class Enable2FASerializer(serializers.Serializer):
    """Serializer para habilitar 2FA."""
    
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate_password(self, value):
        """Valida la contraseña actual del usuario."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña incorrecta.')
        return value


class Verify2FASerializer(serializers.Serializer):
    """Serializer para verificar código 2FA."""
    
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_code(self, value):
        """Valida que el código sea numérico."""
        if not value.isdigit():
            raise serializers.ValidationError('El código debe ser numérico.')
        return value


class GoogleOAuthSerializer(serializers.Serializer):
    """Serializer para autenticación con Google OAuth."""
    
    id_token = serializers.CharField()
    
    def validate_id_token(self, value):
        """Valida el token ID de Google."""
        # Aquí se implementaría la validación del token con Google
        # Por ahora retornamos el valor
        return value


class SocialAccountLinkSerializer(serializers.Serializer):
    """Serializer para vincular cuentas sociales."""
    
    provider = serializers.ChoiceField(choices=['google', 'facebook', 'github'])
    access_token = serializers.CharField()
    
    def validate(self, attrs):
        """Validación de vinculación de cuenta social."""
        provider = attrs.get('provider')
        access_token = attrs.get('access_token')
        
        # Aquí se implementaría la validación específica del proveedor
        
        return attrs

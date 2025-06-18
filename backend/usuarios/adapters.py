"""
Adaptadores personalizados para django-allauth.
Maneja el comportamiento de registro y autenticación social.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpResponseRedirect
from usuarios.models import CustomUser


class AccountAdapter(DefaultAccountAdapter):
    """Adaptador personalizado para manejar cuentas regulares."""
    
    def get_login_redirect_url(self, request):
        """Redirige al frontend después del login."""
        return settings.LOGIN_REDIRECT_URL
    
    def clean_username(self, username, shallow=False):
        """
        Valida el username. Como usamos email, retornamos el username tal como está.
        Esto evita problemas con validaciones de username que no aplican a email.
        """
        return username


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adaptador personalizado para manejar autenticación social."""
    
    def pre_social_login(self, request, sociallogin):
        """
        Invocado justo después de que un usuario se autentica exitosamente con un proveedor social,
        pero antes de que la cuenta se conecte a un usuario local.
        """
        if sociallogin.is_existing:
            return
        
        # Verificar si ya existe un usuario con el mismo email
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            try:
                existing_user = CustomUser.objects.get(email=email)
                
                # Asignar el usuario existente al sociallogin
                sociallogin.user = existing_user
                
                # Actualizar campos sociales si no está marcado como cuenta social
                if not existing_user.is_social_account:
                    existing_user.is_social_account = True
                    existing_user.social_provider = sociallogin.account.provider
                    existing_user.email_verified = True
                    existing_user.save()
                
            except CustomUser.DoesNotExist:
                # No existe usuario con este email, se creará uno nuevo
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Guarda un nuevo usuario (social) en la base de datos.
        """
        user = sociallogin.user
        user.set_unusable_password()
        
        # Configurar campos específicos para cuenta social
        user.is_social_account = True
        user.social_provider = sociallogin.account.provider
        user.email_verified = True
        user.is_active = True
        
        # IMPORTANTE: Asegurar que NO tenga permisos de administrador por defecto
        user.is_staff = False
        user.is_superuser = False
        
        # Obtener información adicional del proveedor
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            if 'given_name' in extra_data:
                user.first_name = extra_data.get('given_name', '')
            if 'family_name' in extra_data:
                user.last_name = extra_data.get('family_name', '')
        user.save()
        return user
    
    def populate_username(self, request, user):
        """
        Genera un username para el usuario social.
        Como usamos email como USERNAME_FIELD, retornamos el email.
        """
        return user.email
    
    def get_login_redirect_url(self, request):
        """Redirige al frontend después del login social."""
        redirect_url = settings.LOGIN_REDIRECT_URL
        print(f"SocialAccountAdapter: Redirigiendo a {redirect_url}")
        print(f"Usuario autenticado: {request.user.is_authenticated if hasattr(request, 'user') else 'Sin usuario'}")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        return redirect_url
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Maneja errores de autenticación."""
        print(f"Error de autenticación social: {error}, {exception}")
        return super().authentication_error(request, provider_id, error, exception, extra_context)

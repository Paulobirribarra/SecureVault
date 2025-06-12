"""
Configuración del admin para los modelos de usuario.
Proporciona una interfaz administrativa completa y segura.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomUser, UserProfile, UserSession
from .forms import UserCreationForm, UserChangeForm


class UserProfileInline(admin.StackedInline):
    """Inline para el perfil de usuario."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = (
        'phone_number', 'birth_date', 'avatar',
        'is_profile_public', 'two_factor_enabled'
    )
    readonly_fields = ('two_factor_secret',)


class UserSessionInline(admin.TabularInline):
    """Inline para mostrar sesiones activas del usuario."""
    model = UserSession
    extra = 0
    readonly_fields = (
        'session_key', 'ip_address', 'user_agent',
        'location', 'created_at', 'last_activity',
        'expires_at', 'is_active'
    )
    can_delete = True
    verbose_name_plural = 'Sesiones Activas'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin personalizado para el modelo de usuario."""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = (
        'email', 'first_name', 'last_name', 'is_active',
        'is_staff', 'email_verified', 'is_social_account',
        'last_login', 'failed_login_attempts', 'account_status'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active',
        'email_verified', 'is_social_account',
        'social_provider', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Permisos'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        (_('Verificación y Seguridad'), {
            'fields': (
                'email_verified', 'email_verification_token',
                'failed_login_attempts', 'account_locked_until'
            )
        }),
        (_('Cuentas Sociales'), {
            'fields': ('is_social_account', 'social_provider')
        }),
        (_('Fechas Importantes'), {
            'fields': ('last_login', 'date_joined', 'password_changed_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name',
                'password1', 'password2', 'is_active',
                'is_staff', 'is_superuser'
            ),
        }),
    )
    
    readonly_fields = (
        'date_joined', 'last_login', 'password_changed_at',
        'email_verification_token'
    )
    
    inlines = [UserProfileInline, UserSessionInline]
    
    def account_status(self, obj):
        """Muestra el estado de la cuenta con colores."""
        if obj.is_account_locked():
            return format_html(
                '<span style="color: red; font-weight: bold;">🔒 Bloqueada</span>'
            )
        elif not obj.email_verified:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠️ Sin verificar</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Activa</span>'
            )
        else:
            return format_html(
                '<span style="color: gray; font-weight: bold;">❌ Inactiva</span>'
            )
    
    account_status.short_description = 'Estado de la Cuenta'
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo el perfil."""
        return super().get_queryset(request).select_related('profile')
    
    actions = ['unlock_accounts', 'verify_emails', 'deactivate_users']
    
    def unlock_accounts(self, request, queryset):
        """Acción para desbloquear cuentas seleccionadas."""
        count = 0
        for user in queryset:
            if user.is_account_locked():
                user.unlock_account()
                count += 1
        
        self.message_user(
            request,
            f'Se desbloquearon {count} cuentas exitosamente.'
        )
    unlock_accounts.short_description = 'Desbloquear cuentas seleccionadas'
    
    def verify_emails(self, request, queryset):
        """Acción para verificar emails manualmente."""
        count = queryset.filter(email_verified=False).update(email_verified=True)
        self.message_user(
            request,
            f'Se verificaron {count} emails exitosamente.'
        )
    verify_emails.short_description = 'Verificar emails seleccionados'
    
    def deactivate_users(self, request, queryset):
        """Acción para desactivar usuarios."""
        count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(
            request,
            f'Se desactivaron {count} usuarios exitosamente.'
        )
    deactivate_users.short_description = 'Desactivar usuarios seleccionados'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para perfiles de usuario."""
    
    list_display = (
        'user_email', 'phone_number', 'birth_date',
        'is_profile_public', 'two_factor_enabled',
        'created_at'
    )
    list_filter = (
        'is_profile_public', 'two_factor_enabled',
        'created_at', 'updated_at'
    )
    search_fields = (
        'user__email', 'user__first_name',
        'user__last_name', 'phone_number'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def user_email(self, obj):
        """Muestra el email del usuario."""
        return obj.user.email
    user_email.short_description = 'Email del Usuario'
    user_email.admin_order_field = 'user__email'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin para sesiones de usuario."""
    
    list_display = (
        'user_email', 'ip_address', 'location',
        'created_at', 'last_activity', 'is_active',
        'session_status'
    )
    list_filter = (
        'is_active', 'created_at', 'expires_at'
    )
    search_fields = (
        'user__email', 'ip_address', 'location',
        'session_key'
    )
    readonly_fields = (
        'session_key', 'user_agent', 'created_at',
        'last_activity'
    )
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Muestra el email del usuario."""
        return obj.user.email
    user_email.short_description = 'Usuario'
    user_email.admin_order_field = 'user__email'
    
    def session_status(self, obj):
        """Muestra el estado de la sesión."""
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">⏰ Expirada</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: green;">🟢 Activa</span>'
            )
        else:
            return format_html(
                '<span style="color: gray;">⭕ Terminada</span>'
            )
    session_status.short_description = 'Estado'
    
    actions = ['terminate_sessions', 'extend_sessions']
    
    def terminate_sessions(self, request, queryset):
        """Termina las sesiones seleccionadas."""
        count = 0
        for session in queryset.filter(is_active=True):
            session.terminate()
            count += 1
        
        self.message_user(
            request,
            f'Se terminaron {count} sesiones exitosamente.'
        )
    terminate_sessions.short_description = 'Terminar sesiones seleccionadas'
    
    def extend_sessions(self, request, queryset):
        """Extiende las sesiones activas por 24 horas."""
        count = 0
        for session in queryset.filter(is_active=True):
            if not session.is_expired():
                session.extend_session()
                count += 1
        
        self.message_user(
            request,
            f'Se extendieron {count} sesiones por 24 horas.'
        )
    extend_sessions.short_description = 'Extender sesiones seleccionadas por 24h'


# Personalización del admin site
admin.site.site_header = "Secure App - Administración"
admin.site.site_title = "Secure App Admin"
admin.site.index_title = "Panel de Administración Segura"

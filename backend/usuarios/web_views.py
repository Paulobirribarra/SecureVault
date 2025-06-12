"""
Vistas web para el panel de administración web.
Estas vistas manejan las páginas HTML del sistema.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView as BaseLoginView
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django_ratelimit.decorators import ratelimit
import secrets
import pyotp
import qrcode
import io
import base64
import logging

from .models import CustomUser, UserProfile, UserSession
from .forms import UserRegistrationForm, UserLoginForm

logger = logging.getLogger(__name__)


class WebLoginView(BaseLoginView):
    """Vista web para login."""
    form_class = UserLoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:dashboard')
    
    @method_decorator(ratelimit(key='ip', rate='10/5m', method='POST'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Procesa el login exitoso."""
        email = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me', False)
        totp_code = form.cleaned_data.get('totp_code')
        
        user = authenticate(self.request, email=email, password=password)
        
        if user:
            # Verificaciones de seguridad
            if not user.is_active:
                messages.error(self.request, 'Tu cuenta está desactivada.')
                return self.form_invalid(form)
            
            if user.is_account_locked():
                messages.error(self.request, 'Tu cuenta está temporalmente bloqueada por intentos fallidos.')
                return self.form_invalid(form)
            
            if not user.email_verified:
                messages.warning(self.request, 'Debes verificar tu email antes de continuar.')
                return redirect('auth:resend-verification-web')
            
            # Verificar 2FA si está habilitado
            if user.profile.two_factor_enabled:
                if not totp_code:
                    messages.error(self.request, 'Código de autenticación de dos factores requerido.')
                    return self.form_invalid(form)
                
                totp = pyotp.TOTP(user.profile.two_factor_secret)
                if not totp.verify(totp_code, valid_window=1):
                    messages.error(self.request, 'Código 2FA inválido.')
                    user.increment_failed_login()
                    return self.form_invalid(form)
            
            # Login exitoso
            login(self.request, user)
            user.reset_failed_login()
            
            # Crear sesión
            self.create_user_session(user)
            
            # Configurar duración de sesión
            if remember_me:
                self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                self.request.session.set_expiry(0)  # Expira al cerrar browser
            
            messages.success(self.request, f'¡Bienvenido, {user.get_full_name()}!')
            logger.info(f'Web login successful: {user.email}')
            
            return super().form_valid(form)
        
        else:
            messages.error(self.request, 'Credenciales inválidas.')
            return self.form_invalid(form)
    
    def create_user_session(self, user):
        """Crea registro de sesión de usuario."""
        try:
            ip_address = self.get_client_ip()
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
            
            UserSession.objects.create(
                user=user,
                session_key=self.request.session.session_key or secrets.token_hex(20),
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=timezone.now() + timezone.timedelta(hours=24)
            )
        except Exception as e:
            logger.error(f'Error creating user session: {str(e)}')
    
    def get_client_ip(self):
        """Obtiene la IP del cliente."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR', '0.0.0.0')


class WebRegisterView(FormView):
    """Vista web para registro."""
    form_class = UserRegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('auth:login-web')
    
    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Procesa el registro exitoso."""
        try:
            user = form.save()
            
            # Generar token de verificación
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            user.save(update_fields=['email_verification_token'])
            
            # Enviar email de verificación
            self.send_verification_email(user, token)
            
            messages.success(
                self.request, 
                'Cuenta creada exitosamente. Te hemos enviado un email de verificación.'
            )
            logger.info(f'New user registered (web): {user.email}')
            
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f'Registration error (web): {str(e)}')
            messages.error(self.request, 'Error al crear la cuenta. Intenta de nuevo.')
            return self.form_invalid(form)
    
    def send_verification_email(self, user, token):
        """Envía email de verificación."""
        try:
            current_site = get_current_site(self.request)
            verification_url = f"http://{current_site.domain}/auth/verify-email/?token={token}&email={user.email}"
            
            subject = 'Verifica tu cuenta - Secure App'
            message = render_to_string('emails/verify_email.html', {
                'user': user,
                'verification_url': verification_url,
                'site_name': 'Secure App'
            })
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=message,
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f'Error sending verification email: {str(e)}')


class WebLogoutView(RedirectView):
    """Vista web para logout."""
    url = reverse_lazy('core:dashboard')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Terminar sesiones activas
            UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key
            ).update(is_active=False)
            
            logger.info(f'Web logout: {request.user.email}')
            logout(request)
            messages.success(request, 'Has cerrado sesión exitosamente.')
        
        return super().get(request, *args, **kwargs)


class VerifyEmailWebView(TemplateView):
    """Vista web para verificar email."""
    template_name = 'auth/email_verified.html'
    
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        email = request.GET.get('email')
        
        if not token or not email:
            messages.error(request, 'Enlace de verificación inválido.')
            return redirect('auth:login-web')
        
        try:
            user = CustomUser.objects.get(
                email=email,
                email_verification_token=token,
                email_verified=False
            )
            
            # Verificar email
            user.email_verified = True
            user.email_verification_token = None
            user.save(update_fields=['email_verified', 'email_verification_token'])
            
            messages.success(request, '¡Email verificado exitosamente! Ya puedes iniciar sesión.')
            logger.info(f'Email verified (web): {user.email}')
            
            return redirect('auth:login-web')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'Token de verificación inválido o expirado.')
            return redirect('auth:login-web')


class ResendVerificationWebView(TemplateView):
    """Vista web para reenviar verificación."""
    template_name = 'auth/resend_verification.html'
    
    @method_decorator(ratelimit(key='ip', rate='3/h', method='POST'))
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Email requerido.')
            return self.get(request, *args, **kwargs)
        
        try:
            user = CustomUser.objects.get(email=email, email_verified=False)
            
            # Generar nuevo token
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            user.save(update_fields=['email_verification_token'])
            
            # Enviar email
            self.send_verification_email(user, token)
            
            messages.success(request, 'Email de verificación enviado.')
            
        except CustomUser.DoesNotExist:
            # No revelar si el email existe
            messages.success(request, 'Si el email existe y no está verificado, se enviará un nuevo enlace.')
        
        return redirect('auth:login-web')
    
    def send_verification_email(self, user, token):
        """Envía email de verificación."""
        try:
            current_site = get_current_site(self.request)
            verification_url = f"http://{current_site.domain}/auth/verify-email/?token={token}&email={user.email}"
            
            subject = 'Verifica tu cuenta - Secure App'
            message = render_to_string('emails/verify_email.html', {
                'user': user,
                'verification_url': verification_url,
                'site_name': 'Secure App'
            })
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=message,
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f'Error sending verification email: {str(e)}')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista del perfil de usuario."""
    template_name = 'auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context


class SessionsView(LoginRequiredMixin, TemplateView):
    """Vista de sesiones activas."""
    template_name = 'auth/sessions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_activity')
        return context


class SecurityView(LoginRequiredMixin, TemplateView):
    """Vista de configuración de seguridad."""
    template_name = 'auth/security.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['two_factor_enabled'] = self.request.user.profile.two_factor_enabled
        return context


# APIs AJAX para el panel web
@login_required
@csrf_exempt
def enable_2fa_web(request):
    """API para habilitar 2FA desde web."""
    if request.method == 'POST':
        try:
            # Generar secreto 2FA
            secret = pyotp.random_base32()
            
            # Crear código QR
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=request.user.email,
                issuer_name='Secure App'
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Guardar secreto temporalmente
            request.user.profile.two_factor_secret = secret
            request.user.profile.save(update_fields=['two_factor_secret'])
            
            return JsonResponse({
                'success': True,
                'secret': secret,
                'qr_code': f'data:image/png;base64,{img_str}'
            })
            
        except Exception as e:
            logger.error(f'Enable 2FA web error: {str(e)}')
            return JsonResponse({'error': 'Error al habilitar 2FA'})
    
    return JsonResponse({'error': 'Método no permitido'})


@login_required
@csrf_exempt
def verify_2fa_web(request):
    """API para verificar y confirmar 2FA desde web."""
    if request.method == 'POST':
        try:
            code = request.POST.get('code')
            
            if not code:
                return JsonResponse({'error': 'Código requerido'})
            
            # Verificar código
            totp = pyotp.TOTP(request.user.profile.two_factor_secret)
            if totp.verify(code, valid_window=1):
                # Habilitar 2FA permanentemente
                request.user.profile.two_factor_enabled = True
                request.user.profile.save(update_fields=['two_factor_enabled'])
                
                logger.info(f'2FA enabled (web): {request.user.email}')
                
                return JsonResponse({
                    'success': True,
                    'message': '2FA habilitado exitosamente'
                })
            else:
                return JsonResponse({'error': 'Código inválido'})
                
        except Exception as e:
            logger.error(f'Verify 2FA web error: {str(e)}')
            return JsonResponse({'error': 'Error al verificar 2FA'})
    
    return JsonResponse({'error': 'Método no permitido'})


@login_required
@csrf_exempt
def disable_2fa_web(request):
    """API para deshabilitar 2FA desde web."""
    if request.method == 'POST':
        try:
            password = request.POST.get('password')
            
            if not password:
                return JsonResponse({'error': 'Contraseña requerida'})
            
            # Verificar contraseña
            if not request.user.check_password(password):
                return JsonResponse({'error': 'Contraseña incorrecta'})
            
            # Deshabilitar 2FA
            request.user.profile.two_factor_enabled = False
            request.user.profile.two_factor_secret = ''
            request.user.profile.save(update_fields=['two_factor_enabled', 'two_factor_secret'])
            
            logger.info(f'2FA disabled (web): {request.user.email}')
            
            return JsonResponse({
                'success': True,
                'message': '2FA deshabilitado exitosamente'
            })
            
        except Exception as e:
            logger.error(f'Disable 2FA web error: {str(e)}')
            return JsonResponse({'error': 'Error al deshabilitar 2FA'})
    
    return JsonResponse({'error': 'Método no permitido'})


@login_required
@csrf_exempt
def terminate_session_web(request):
    """API para terminar una sesión específica."""
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session_id')
            
            if not session_id:
                return JsonResponse({'error': 'ID de sesión requerido'})
            
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            
            session.terminate()
            
            return JsonResponse({
                'success': True,
                'message': 'Sesión terminada exitosamente'
            })
            
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Sesión no encontrada'})
        except Exception as e:
            logger.error(f'Terminate session web error: {str(e)}')
            return JsonResponse({'error': 'Error al terminar sesión'})
    
    return JsonResponse({'error': 'Método no permitido'})

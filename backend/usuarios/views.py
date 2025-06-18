"""
Vistas para el sistema de autenticación segura y gestión de usuarios.
Implementa JWT, verificación de email, 2FA y gestión de sesiones.
"""

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import secrets
import logging
import pyotp
import qrcode
import io
import base64
from datetime import timedelta

from .models import CustomUser, UserProfile, UserSession
from .forms import (
    UserRegistrationForm, UserLoginForm, PasswordResetForm,
    PasswordResetConfirmForm
)
from .serializers import (
    UserSerializer, UserProfileSerializer, UserSessionSerializer,
    RegisterSerializer, LoginSerializer, PasswordChangeSerializer
)
from django.shortcuts import redirect
import secrets

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """Vista para registro de nuevos usuarios."""
    
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST'))
    def post(self, request):
        """Registra un nuevo usuario."""
        try:
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generar token de verificación
                    token = secrets.token_urlsafe(32)
                    user.email_verification_token = token
                    user.save(update_fields=['email_verification_token'])
                    
                    # Enviar email de verificación
                    self.send_verification_email(request, user, token)
                    
                    logger.info(f'New user registered: {user.email}')
                    
                    return Response({
                        'message': 'Usuario registrado exitosamente. Por favor verifica tu email.',
                        'user_id': str(user.id),
                        'email': user.email
                    }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f'Registration error: {str(e)}')
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_verification_email(self, request, user, token):
        """Envía email de verificación."""
        try:
            current_site = get_current_site(request)
            verification_url = f"http://{current_site.domain}/api/v1/usuarios/auth/verify-email/?token={token}&email={user.email}"
            
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


class LoginView(APIView):
    """Vista para autenticación de usuarios."""
    
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/5m', method='POST'))
    def post(self, request):
        """Autentica un usuario y retorna tokens JWT."""
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                remember_me = serializer.validated_data.get('remember_me', False)
                
                # Autenticar usuario
                user = authenticate(request, email=email, password=password)
                
                if user:
                    # Verificar estado de la cuenta
                    if not user.is_active:
                        return Response({
                            'error': 'Cuenta desactivada'
                        }, status=status.HTTP_403_FORBIDDEN)
                    
                    if user.is_account_locked():
                        return Response({
                            'error': 'Cuenta temporalmente bloqueada'
                        }, status=status.HTTP_423_LOCKED)
                    
                    if not user.email_verified:
                        return Response({
                            'error': 'Email no verificado',
                            'requires_verification': True
                        }, status=status.HTTP_403_FORBIDDEN)
                    
                    # Verificar 2FA si está habilitado
                    if user.profile.two_factor_enabled:
                        totp_code = request.data.get('totp_code')
                        if not totp_code:
                            return Response({
                                'error': 'Código 2FA requerido',
                                'requires_2fa': True
                            }, status=status.HTTP_206_PARTIAL_CONTENT)
                        
                        if not self.verify_2fa_code(user, totp_code):
                            user.increment_failed_login()
                            return Response({
                                'error': 'Código 2FA inválido'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Generar tokens JWT
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    # Configurar duración del refresh token
                    if remember_me:
                        refresh.set_exp(lifetime=timedelta(days=30))
                    
                    # Crear sesión de usuario
                    self.create_user_session(request, user)
                    
                    # Login exitoso
                    login(request, user)
                    user.reset_failed_login()
                    
                    logger.info(f'Successful login: {user.email}')
                    
                    return Response({
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data,
                        'expires_in': int(access_token.payload['exp'] - access_token.current_time.timestamp())
                    }, status=status.HTTP_200_OK)
                
                else:
                    # Login fallido
                    try:
                        user = CustomUser.objects.get(email=email)
                        user.increment_failed_login()
                    except CustomUser.DoesNotExist:
                        pass
                    
                    logger.warning(f'Failed login attempt: {email}')
                    
                    return Response({
                        'error': 'Credenciales inválidas'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def verify_2fa_code(self, user, code):
        """Verifica el código TOTP 2FA."""
        try:
            totp = pyotp.TOTP(user.profile.two_factor_secret)
            return totp.verify(code, valid_window=1)
        except Exception:
            return False
    
    def create_user_session(self, request, user):
        """Crea un registro de sesión de usuario."""
        try:
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key or secrets.token_hex(20),
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
        except Exception as e:
            logger.error(f'Error creating user session: {str(e)}')
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


class LogoutView(APIView):
    """Vista para cerrar sesión."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cierra la sesión del usuario."""
        try:
            # Obtener token de refresh
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                # Invalidar token de refresh
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Terminar sesión de usuario
            if hasattr(request, 'session') and request.session.session_key:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=request.session.session_key
                ).update(is_active=False)
            
            # Logout de Django
            logout(request)
            
            logger.info(f'User logged out: {request.user.email}')
            
            return Response({
                'message': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Logout error: {str(e)}')
            return Response({
                'error': 'Error al cerrar sesión'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshTokenView(TokenRefreshView):
    """Vista personalizada para renovar tokens JWT."""
    
    def post(self, request, *args, **kwargs):
        """Renueva el token de acceso."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f'Token refreshed for user session')
        
        return response


class VerifyEmailView(APIView):
    """Vista para verificar email de usuario."""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Verifica el email usando el token."""
        try:
            token = request.GET.get('token')
            email = request.GET.get('email')
            
            if not token or not email:
                return Response({
                    'error': 'Token y email requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar usuario
            try:
                user = CustomUser.objects.get(
                    email=email,
                    email_verification_token=token,
                    email_verified=False
                )
            except CustomUser.DoesNotExist:
                return Response({
                    'error': 'Token de verificación inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar email
            user.email_verified = True
            user.email_verification_token = None
            user.save(update_fields=['email_verified', 'email_verification_token'])
            
            logger.info(f'Email verified for user: {user.email}')
            
            return Response({
                'message': 'Email verificado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Email verification error: {str(e)}')
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationView(APIView):
    """Vista para reenviar email de verificación."""
    
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/h', method='POST'))
    def post(self, request):
        """Reenvía email de verificación."""
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({
                    'error': 'Email requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = CustomUser.objects.get(email=email, email_verified=False)
            except CustomUser.DoesNotExist:
                # No revelar si el email existe
                return Response({
                    'message': 'Si el email existe y no está verificado, se enviará un nuevo enlace'
                }, status=status.HTTP_200_OK)
            
            # Generar nuevo token
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            user.save(update_fields=['email_verification_token'])
            
            # Enviar email
            self.send_verification_email(request, user, token)
            
            return Response({
                'message': 'Email de verificación enviado'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Resend verification error: {str(e)}')
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_verification_email(self, request, user, token):
        """Envía email de verificación."""
        try:
            current_site = get_current_site(request)
            verification_url = f"http://{current_site.domain}/api/v1/usuarios/auth/verify-email/?token={token}&email={user.email}"
            
            subject = 'Verifica tu cuenta - Secure App'
            message = f"""
            Hola {user.get_full_name()},
            
            Para verificar tu cuenta, haz clic en el siguiente enlace:
            {verification_url}
            
            Si no solicitaste esta verificación, ignora este email.
            
            Saludos,
            El equipo de Secure App
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f'Error sending verification email: {str(e)}')


class CurrentUserView(APIView):
    """Vista para obtener información del usuario actual."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retorna información del usuario autenticado."""
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Current user error: {str(e)}')
            return Response({
                'error': 'Error al obtener información del usuario'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordChangeView(APIView):
    """Vista para cambio de contraseña."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cambia la contraseña del usuario."""
        try:
            serializer = PasswordChangeSerializer(data=request.data)
            
            if serializer.is_valid():
                old_password = serializer.validated_data['old_password']
                new_password = serializer.validated_data['new_password']
                
                # Verificar contraseña actual
                if not request.user.check_password(old_password):
                    return Response({
                        'error': 'Contraseña actual incorrecta'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Cambiar contraseña
                request.user.set_password(new_password)
                request.user.password_changed_at = timezone.now()
                request.user.save(update_fields=['password', 'password_changed_at'])
                
                logger.info(f'Password changed for user: {request.user.email}')
                
                return Response({
                    'message': 'Contraseña cambiada exitosamente'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f'Password change error: {str(e)}')
            return Response({
                'error': 'Error al cambiar contraseña'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Enable2FAView(APIView):
    """Vista para habilitar autenticación de dos factores."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Habilita 2FA para el usuario."""
        try:
            if request.user.profile.two_factor_enabled:
                return Response({
                    'error': '2FA ya está habilitado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar secreto TOTP
            secret = pyotp.random_base32()
            
            # Crear código QR
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=request.user.email,
                issuer_name='Secure App'
            )
            
            # Generar QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Guardar secreto temporalmente (se confirmará con verificación)
            request.user.profile.two_factor_secret = secret
            request.user.profile.save(update_fields=['two_factor_secret'])
            
            return Response({
                'secret': secret,
                'qr_code': f'data:image/png;base64,{img_str}',
                'manual_entry_key': secret
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Enable 2FA error: {str(e)}')
            return Response({
                'error': 'Error al habilitar 2FA'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Verify2FAView(APIView):
    """Vista para verificar y confirmar 2FA."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verifica el código 2FA y confirma la activación."""
        try:
            code = request.data.get('code')
            
            if not code:
                return Response({
                    'error': 'Código requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar código
            totp = pyotp.TOTP(request.user.profile.two_factor_secret)
            if totp.verify(code, valid_window=1):
                # Activar 2FA
                request.user.profile.two_factor_enabled = True
                request.user.profile.save(update_fields=['two_factor_enabled'])
                
                logger.info(f'2FA enabled for user: {request.user.email}')
                
                return Response({
                    'message': '2FA habilitado exitosamente'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Código inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f'Verify 2FA error: {str(e)}')
            return Response({
                'error': 'Error al verificar 2FA'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de perfiles de usuario."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo permite acceso al perfil del usuario autenticado."""
        return UserProfile.objects.filter(user=self.request.user)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar sesiones activas del usuario."""
    
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo sesiones del usuario autenticado."""
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_activity')
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Termina una sesión específica."""
        try:
            session = self.get_object()
            session.terminate()
            
            logger.info(f'Session terminated: {session.session_key}')
            
            return Response({
                'message': 'Sesión terminada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Terminate session error: {str(e)}')
            return Response({
                'error': 'Error al terminar sesión'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialLoginRedirectView(APIView):
    """Vista para manejar la redirección después del login social."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Redirige al frontend con tokens JWT después del login social."""
        if request.user.is_authenticated:
            try:
                # Generar tokens JWT para el usuario
                refresh = RefreshToken.for_user(request.user)
                access_token = refresh.access_token
                  # Crear sesión de usuario
                self.create_user_session(request, request.user)
                
                # Construir URL con tokens para el callback social
                callback_url = f"http://localhost:4200/auth/social-callback?access_token={str(access_token)}&refresh_token={str(refresh)}"
                
                logger.info(f'Social login redirect for user: {request.user.email}')
                return redirect(callback_url)
                
            except Exception as e:
                logger.error(f'Error generating JWT tokens for social login: {str(e)}')
                return redirect('http://localhost:4200/auth/login?error=token_generation_failed')
        else:
            # Error en la autenticación
            logger.warning('Social login redirect without authenticated user')           
        return redirect('http://localhost:4200/auth/login?error=social_login_failed')
    
    def create_user_session(self, request, user):
        """Crea un registro de sesión de usuario con límite de sesiones activas."""
        try:
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            session_key = request.session.session_key or secrets.token_hex(20)
            
            # Terminar sesiones expiradas del usuario
            UserSession.objects.filter(
                user=user,
                expires_at__lt=timezone.now()
            ).update(is_active=False)
            
            # Limitar a máximo 5 sesiones activas por usuario
            active_sessions = UserSession.objects.filter(
                user=user,
                is_active=True
            ).order_by('-last_activity')
            
            if active_sessions.count() >= 5:
                # Terminar las sesiones más antiguas
                old_sessions = active_sessions[4:]
                for session in old_sessions:
                    session.terminate()
            
            # Crear nueva sesión (o actualizar si ya existe)
            session, created = UserSession.objects.get_or_create(
                user=user,
                session_key=session_key,
                defaults={
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'expires_at': timezone.now() + timedelta(hours=24),
                    'is_active': True
                }
            )
            
            if not created:
                # Actualizar sesión existente
                session.ip_address = ip_address
                session.user_agent = user_agent
                session.expires_at = timezone.now() + timedelta(hours=24)
                session.is_active = True
                session.save()
            
        except Exception as e:
            logger.error(f'Error creating user session: {str(e)}')
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


# Vistas adicionales para OAuth, password reset, etc. se pueden agregar aquí

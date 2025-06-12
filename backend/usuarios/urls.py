"""
URLs para el sistema de autenticación y gestión de usuarios.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'usuarios'

# Router para ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'sessions', views.UserSessionViewSet, basename='session')

urlpatterns = [
    # Autenticación básica
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    
    # Verificación de email
    path('auth/verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    
    # Perfil de usuario
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # 2FA (Two Factor Authentication)
    path('auth/2fa/enable/', views.Enable2FAView.as_view(), name='enable-2fa'),
    path('auth/2fa/verify/', views.Verify2FAView.as_view(), name='verify-2fa'),
    
    # ViewSets
    path('', include(router.urls)),
    
    # TODO: Implementar estas vistas más tarde
    # path('auth/password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    # path('auth/password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # path('auth/me/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    # path('auth/me/deactivate/', views.DeactivateAccountView.as_view(), name='deactivate-account'),
    # path('auth/sessions/current/', views.CurrentSessionView.as_view(), name='current-session'),
    # path('auth/sessions/terminate/', views.TerminateSessionView.as_view(), name='terminate-session'),
    # path('auth/sessions/terminate-all/', views.TerminateAllSessionsView.as_view(), name='terminate-all-sessions'),
    # path('auth/2fa/disable/', views.Disable2FAView.as_view(), name='disable-2fa'),
    # path('auth/google/', views.GoogleOAuthView.as_view(), name='google-oauth'),
    # path('auth/google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google-oauth-callback'),
]

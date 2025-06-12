"""
Vistas web para el sistema de baúl de contraseñas.
Incluye tanto vistas de plantillas como APIs REST.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import secrets
import string
import json

from .models import VaultItem, VaultFolder, VaultActivity, MasterPasswordHash
from .crypto import AESCrypto, VaultEntry


class DashboardView(TemplateView):
    """Vista principal del dashboard."""
    
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Estadísticas del baúl
            vault_stats = {
                'total_items': VaultItem.objects.filter(user=self.request.user).count(),
                'login_items': VaultItem.objects.filter(
                    user=self.request.user, 
                    item_type='login'
                ).count(),
                'secure_notes': VaultItem.objects.filter(
                    user=self.request.user, 
                    item_type='note'
                ).count(),
            }
            
            # Entradas recientes
            recent_items = VaultItem.objects.filter(
                user=self.request.user
            ).order_by('-updated_at')[:5]
            
            # Puntuación de seguridad básica
            security_score = self.calculate_security_score()
            
            context.update({
                'vault_stats': vault_stats,
                'recent_items': recent_items,
                'security_score': security_score,
                'current_year': timezone.now().year,
            })
        
        return context
    
    def calculate_security_score(self):
        """Calcula una puntuación básica de seguridad."""
        score = 0
        user = self.request.user
        
        # Email verificado: +20 puntos
        if user.email_verified:
            score += 20
        
        # 2FA habilitado: +30 puntos
        if hasattr(user, 'profile') and user.profile.two_factor_enabled:
            score += 30
        
        # Tiene entradas en el baúl: +20 puntos
        if VaultItem.objects.filter(user=user).exists():
            score += 20
        
        # Contraseña maestra configurada: +30 puntos
        if MasterPasswordHash.objects.filter(user=user).exists():
            score += 30
        
        return min(score, 100)


class VaultView(LoginRequiredMixin, TemplateView):
    """Vista del baúl de contraseñas."""
    
    template_name = 'vault/vault.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener carpetas del usuario
        folders = VaultFolder.objects.filter(user=self.request.user).order_by('name')
        
        # Obtener entradas del baúl (sin descifrar)
        vault_items = VaultItem.objects.filter(
            user=self.request.user
        ).select_related('folder').order_by('-updated_at')
        
        # Filtros
        item_type = self.request.GET.get('type')
        folder_id = self.request.GET.get('folder')
        search = self.request.GET.get('search')
        
        if item_type:
            vault_items = vault_items.filter(item_type=item_type)
        
        if folder_id:
            vault_items = vault_items.filter(folder_id=folder_id)
        
        if search:
            vault_items = vault_items.filter(name__icontains=search)
        
        context.update({
            'folders': folders,
            'vault_items': vault_items,
            'current_type': item_type,
            'current_folder': folder_id,
            'search_query': search,
        })
        
        return context


class PasswordGeneratorView(TemplateView):
    """Vista del generador de contraseñas."""
    
    template_name = 'vault/password_generator.html'


class SecurityCenterView(LoginRequiredMixin, TemplateView):
    """Vista del centro de seguridad."""
    
    template_name = 'vault/security_center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Análisis básico de seguridad
        security_analysis = {
            'total_items': VaultItem.objects.filter(user=self.request.user).count(),
            'weak_passwords': 0,  # Calcular después
            'duplicate_passwords': 0,  # Calcular después
            'old_passwords': 0,  # Calcular después
        }
        
        context.update({
            'security_analysis': security_analysis,
        })
        
        return context


# APIs para AJAX
@csrf_exempt
def generate_password_api(request):
    """API para generar contraseñas."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            length = int(data.get('length', 16))
            include_uppercase = data.get('include_uppercase', True)
            include_lowercase = data.get('include_lowercase', True)
            include_numbers = data.get('include_numbers', True)
            include_symbols = data.get('include_symbols', True)
            exclude_ambiguous = data.get('exclude_ambiguous', True)
            
            # Validar parámetros
            if length < 4 or length > 128:
                return JsonResponse({'error': 'La longitud debe estar entre 4 y 128 caracteres'})
            
            # Construir conjunto de caracteres
            chars = ''
            if include_lowercase:
                chars += string.ascii_lowercase
            if include_uppercase:
                chars += string.ascii_uppercase
            if include_numbers:
                chars += string.digits
            if include_symbols:
                chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'
            
            if exclude_ambiguous:
                # Excluir caracteres ambiguos
                ambiguous = 'il1Lo0O'
                chars = ''.join(c for c in chars if c not in ambiguous)
            
            if not chars:
                return JsonResponse({'error': 'Debes seleccionar al menos un tipo de carácter'})
            
            # Generar contraseña
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            # Calcular fortaleza
            strength = calculate_password_strength(password)
            
            return JsonResponse({
                'password': password,
                'strength': strength,
                'length': len(password)
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error al generar contraseña: {str(e)}'})
    
    return JsonResponse({'error': 'Método no permitido'})


def calculate_password_strength(password):
    """Calcula la fortaleza de una contraseña."""
    score = 0
    feedback = []
    
    # Longitud
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Complejidad
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 1
    
    # Determinar nivel
    if score >= 5:
        level = 'very_strong'
    elif score >= 4:
        level = 'strong'
    elif score >= 3:
        level = 'medium'
    elif score >= 2:
        level = 'weak'
    else:
        level = 'very_weak'
    
    return {
        'score': score,
        'level': level,
        'percentage': min(100, (score / 6) * 100)
    }


@login_required
def vault_status_api(request):
    """API para obtener estado del baúl."""
    try:
        # Verificar si el usuario tiene contraseña maestra
        has_master_password = MasterPasswordHash.objects.filter(
            user=request.user
        ).exists()
        
        # Verificar si el baúl está "desbloqueado" en la sesión
        vault_unlocked = request.session.get('vault_unlocked', False)
        
        return JsonResponse({
            'has_master_password': has_master_password,
            'vault_unlocked': vault_unlocked,
            'total_items': VaultItem.objects.filter(user=request.user).count(),
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error al obtener estado: {str(e)}'})


@login_required
def unlock_vault_api(request):
    """API para desbloquear el baúl con contraseña maestra."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            master_password = data.get('master_password')
            
            if not master_password:
                return JsonResponse({'error': 'Contraseña maestra requerida'})
            
            # Verificar contraseña maestra
            try:
                master_hash = MasterPasswordHash.objects.get(user=request.user)
                if master_hash.verify_password(master_password):
                    # Marcar baúl como desbloqueado en la sesión
                    request.session['vault_unlocked'] = True
                    request.session['vault_unlock_time'] = timezone.now().isoformat()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Baúl desbloqueado exitosamente'
                    })
                else:
                    return JsonResponse({'error': 'Contraseña maestra incorrecta'})
                    
            except MasterPasswordHash.DoesNotExist:
                return JsonResponse({'error': 'Contraseña maestra no configurada'})
            
        except Exception as e:
            return JsonResponse({'error': f'Error al desbloquear: {str(e)}'})
    
    return JsonResponse({'error': 'Método no permitido'})


@login_required
def lock_vault_api(request):
    """API para bloquear el baúl."""
    if request.method == 'POST':
        # Eliminar estado de desbloqueo de la sesión
        request.session.pop('vault_unlocked', None)
        request.session.pop('vault_unlock_time', None)
        
        return JsonResponse({
            'success': True,
            'message': 'Baúl bloqueado exitosamente'
        })
    
    return JsonResponse({'error': 'Método no permitido'})


# Vistas temporales para desarrollo
def not_implemented_view(request):
    """Vista temporal para endpoints no implementados."""
    return render(request, 'base/not_implemented.html')

"""
URLs para el sistema de baúl de contraseñas cifrado.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse

app_name = 'core'

# Función temporal para endpoints no implementados
def not_implemented(request):
    return JsonResponse({
        'message': 'Endpoint en desarrollo',
        'status': 'TODO'
    })

urlpatterns = [
    # Endpoints temporales
    path('vault/status/', not_implemented, name='vault-status'),
    path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health'),
    
    # TODO: Implementar vistas del baúl
    # path('vault/master-password/set/', views.SetMasterPasswordView.as_view(), name='set-master-password'),
    # path('vault/master-password/verify/', views.VerifyMasterPasswordView.as_view(), name='verify-master-password'),
    # path('vault/unlock/', views.UnlockVaultView.as_view(), name='unlock-vault'),
    # path('vault/lock/', views.LockVaultView.as_view(), name='lock-vault'),
]

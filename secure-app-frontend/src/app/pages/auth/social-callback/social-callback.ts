import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
    selector: 'app-social-callback',
    template: `
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-purple-900">
      <div class="text-center text-white">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <h2 class="text-xl font-semibold">Completando autenticación...</h2>
        <p class="text-gray-300 mt-2">Te redirigiremos al dashboard en un momento</p>
      </div>
    </div>
  `,
    standalone: true
})
export class SocialCallback implements OnInit {

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private authService: AuthService,
        private notificationService: NotificationService
    ) { }

    ngOnInit(): void {
        this.processSocialLoginTokens();
    }

    private processSocialLoginTokens(): void {
        this.route.queryParams.subscribe(params => {
            const accessToken = params['access_token'];
            const refreshToken = params['refresh_token'];
            const error = params['error'];

            if (error) {
                this.handleLoginError(error);
                return;
            } if (accessToken && refreshToken) {
                // Usar el método handleSocialLogin del AuthService
                this.authService.handleSocialLogin(accessToken, refreshToken).subscribe({
                    next: (user) => {
                        // Mostrar notificación de éxito
                        this.notificationService.success('¡Bienvenido!', 'Has iniciado sesión con Google correctamente');

                        // Redirigir al dashboard
                        this.router.navigate(['/dashboard'], { replaceUrl: true });
                    },
                    error: (error) => {
                        console.error('Error during social login:', error);
                        this.notificationService.error('Error', 'No se pudo completar el login social');
                        this.router.navigate(['/auth/login'], { replaceUrl: true });
                    }
                });
            } else {
                // No hay tokens, redirigir a login
                this.notificationService.error('Error', 'No se recibieron los tokens de autenticación');
                this.router.navigate(['/auth/login'], { replaceUrl: true });
            }
        });
    }

    private handleLoginError(error: string): void {
        let message = 'Error durante el login social';

        switch (error) {
            case 'social_login_failed':
                message = 'Error en la autenticación con Google';
                break;
            case 'token_generation_failed':
                message = 'Error al generar tokens de acceso';
                break;
            default:
                message = 'Error desconocido durante el login';
        }

        this.notificationService.error('Error de autenticación', message);
        this.router.navigate(['/auth/login'], { replaceUrl: true });
    }
}

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import {
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    RegisterRequest,
    RegisterResponse,
    User
} from '../models';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly API_URL = 'http://localhost:8000/api/v1/usuarios';
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);

    public currentUser$ = this.currentUserSubject.asObservable();
    public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

    constructor(private http: HttpClient) {
        // Verificar si hay token almacenado al iniciar
        this.checkStoredAuth();
    }

    /**
     * Inicia sesión del usuario
     */
    login(loginData: LoginRequest): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.API_URL}/auth/login/`, loginData)
            .pipe(
                tap(response => {
                    this.setSession(response);
                }),
                catchError(this.handleError)
            );
    }

    /**
     * Registra un nuevo usuario
     */
    register(registerData: RegisterRequest): Observable<RegisterResponse> {
        return this.http.post<RegisterResponse>(`${this.API_URL}/auth/register/`, registerData)
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Cierra sesión del usuario
     */
    logout(): Observable<any> {
        const refreshToken = this.getRefreshToken();
        const body = refreshToken ? { refresh: refreshToken } : {};

        return this.http.post(`${this.API_URL}/auth/logout/`, body)
            .pipe(
                tap(() => {
                    this.clearSession();
                }),
                catchError(() => {
                    // Incluso si el logout falla en el backend, limpiamos la sesión local
                    this.clearSession();
                    return throwError(() => new Error('Error al cerrar sesión'));
                })
            );
    }

    /**
     * Renueva el token de acceso
     */
    refreshToken(): Observable<any> {
        const refreshToken = this.getRefreshToken();

        if (!refreshToken) {
            return throwError(() => new Error('No refresh token available'));
        }

        return this.http.post(`${this.API_URL}/auth/refresh/`, { refresh: refreshToken })
            .pipe(
                tap((response: any) => {
                    if (response.access) {
                        localStorage.setItem('access_token', response.access);
                    }
                }),
                catchError(error => {
                    this.clearSession();
                    return throwError(() => error);
                })
            );
    }

    /**
     * Obtiene información del usuario actual
     */
    getCurrentUser(): Observable<User> {
        return this.http.get<User>(`${this.API_URL}/auth/me/`)
            .pipe(
                tap(user => {
                    this.currentUserSubject.next(user);
                }),
                catchError(this.handleError)
            );
    }

    /**
     * Cambia la contraseña del usuario
     */
    changePassword(passwordData: PasswordChangeRequest): Observable<any> {
        return this.http.post(`${this.API_URL}/auth/password-change/`, passwordData)
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Verifica el email del usuario
     */
    verifyEmail(token: string, email: string): Observable<any> {
        return this.http.get(`${this.API_URL}/auth/verify-email/?token=${token}&email=${email}`)
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Reenvía email de verificación
     */
    resendVerification(email: string): Observable<any> {
        return this.http.post(`${this.API_URL}/auth/resend-verification/`, { email })
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Habilita 2FA para el usuario
     */
    enable2FA(): Observable<any> {
        return this.http.post(`${this.API_URL}/auth/2fa/enable/`, {})
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Verifica código 2FA
     */
    verify2FA(code: string): Observable<any> {
        return this.http.post(`${this.API_URL}/auth/2fa/verify/`, { code })
            .pipe(
                catchError(this.handleError)
            );
    }

    /**
     * Obtiene el token de acceso
     */
    getAccessToken(): string | null {
        return localStorage.getItem('access_token');
    }

    /**
     * Obtiene el token de refresh
     */
    getRefreshToken(): string | null {
        return localStorage.getItem('refresh_token');
    }

    /**
     * Verifica si el usuario está autenticado
     */
    isAuthenticated(): boolean {
        const token = this.getAccessToken();
        return !!token && !this.isTokenExpired(token);
    }

    /**
     * Verifica si el token ha expirado
     */
    private isTokenExpired(token: string): boolean {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            return payload.exp < currentTime;
        } catch {
            return true;
        }
    }

    /**
     * Establece la sesión del usuario
     */
    private setSession(authResult: LoginResponse): void {
        localStorage.setItem('access_token', authResult.access);
        localStorage.setItem('refresh_token', authResult.refresh);

        this.currentUserSubject.next(authResult.user);
        this.isAuthenticatedSubject.next(true);

        // Configurar renovación automática del token
        this.scheduleTokenRefresh(authResult.expires_in);
    }

    /**
     * Limpia la sesión del usuario
     */
    private clearSession(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        this.currentUserSubject.next(null);
        this.isAuthenticatedSubject.next(false);
    }

    /**
     * Verifica autenticación almacenada al iniciar
     */
    private checkStoredAuth(): void {
        const token = this.getAccessToken();

        if (token && !this.isTokenExpired(token)) {
            this.isAuthenticatedSubject.next(true);

            // Obtener información del usuario
            this.getCurrentUser().subscribe({
                next: () => {
                    // Usuario cargado exitosamente
                },
                error: () => {
                    this.clearSession();
                }
            });
        } else {
            this.clearSession();
        }
    }

    /**
     * Programa la renovación automática del token
     */
    private scheduleTokenRefresh(expiresIn: number): void {
        // Renovar 30 segundos antes de que expire
        const refreshTime = (expiresIn - 30) * 1000;

        setTimeout(() => {
            if (this.isAuthenticated()) {
                this.refreshToken().subscribe({
                    next: () => {
                        // Token renovado exitosamente
                    },
                    error: () => {
                        this.clearSession();
                    }
                });
            }
        }, refreshTime);
    }

    /**
     * Maneja errores de la API
     */
    private handleError = (error: any): Observable<never> => {
        let errorMessage = 'Error desconocido';

        if (error.error instanceof ErrorEvent) {
            // Error del lado del cliente
            errorMessage = error.error.message;
        } else {
            // Error del lado del servidor
            if (error.error && error.error.error) {
                errorMessage = error.error.error;
            } else if (error.error && typeof error.error === 'string') {
                errorMessage = error.error;
            } else if (error.message) {
                errorMessage = error.message;
            }
        }

        console.error('AuthService Error:', error);
        return throwError(() => ({ error: errorMessage, details: error }));
    };
}

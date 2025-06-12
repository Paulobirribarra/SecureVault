import { HttpErrorResponse, HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, filter, switchMap, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

let isRefreshing = false;
let refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn): Observable<HttpEvent<any>> => {
    const authService = inject(AuthService);

    // Agregar token de autorización si está disponible
    let authReq = req;
    const token = authService.getAccessToken();

    if (token && !req.url.includes('/auth/login') && !req.url.includes('/auth/register')) {
        authReq = addTokenHeader(req, token);
    }

    return next(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status === 401 && !req.url.includes('/auth/login')) {
                return handle401Error(authReq, next, authService);
            }

            return throwError(() => error);
        })
    );
};

function addTokenHeader(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
        headers: request.headers.set('Authorization', `Bearer ${token}`)
    });
}

function handle401Error(request: HttpRequest<any>, next: HttpHandlerFn, authService: AuthService): Observable<HttpEvent<any>> {
    if (!isRefreshing) {
        isRefreshing = true;
        refreshTokenSubject.next(null);

        const refreshToken = authService.getRefreshToken();

        if (refreshToken) {
            return authService.refreshToken().pipe(
                switchMap((response: any) => {
                    isRefreshing = false;
                    refreshTokenSubject.next(response.access);
                    return next(addTokenHeader(request, response.access));
                }),
                catchError((error) => {
                    isRefreshing = false;
                    authService.logout();
                    return throwError(() => error);
                })
            );
        } else {
            authService.logout();
            return throwError(() => new Error('No refresh token available'));
        }
    }

    return refreshTokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap((token) => next(addTokenHeader(request, token)))
    );
}

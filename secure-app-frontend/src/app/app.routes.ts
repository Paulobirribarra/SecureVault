import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { GuestGuard } from './guards/guest.guard';

export const routes: Routes = [
    // Rutas públicas (guest only)
    {
        path: 'auth/login',
        loadComponent: () => import('./pages/auth/login/login').then(c => c.Login),
        canActivate: [GuestGuard]
    },
    {
        path: 'auth/register',
        loadComponent: () => import('./pages/auth/register/register').then(c => c.Register),
        canActivate: [GuestGuard]
    },

    // Rutas protegidas (authenticated only)
    {
        path: 'dashboard',
        loadComponent: () => import('./pages/dashboard/dashboard').then(c => c.Dashboard),
        canActivate: [AuthGuard]
    },

    // Redirecciones
    {
        path: '',
        redirectTo: '/dashboard',
        pathMatch: 'full'
    },
    {
        path: '**',
        redirectTo: '/dashboard'
    }
];

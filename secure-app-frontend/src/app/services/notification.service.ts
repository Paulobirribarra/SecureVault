import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface Toast {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message?: string;
    duration?: number;
    dismissible?: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    private toastsSubject = new BehaviorSubject<Toast[]>([]);
    public toasts$ = this.toastsSubject.asObservable();

    private generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }

    private addToast(toast: Omit<Toast, 'id'>): void {
        const newToast: Toast = {
            ...toast,
            id: this.generateId(),
            duration: toast.duration ?? 5000,
            dismissible: toast.dismissible ?? true
        };

        const currentToasts = this.toastsSubject.value;
        this.toastsSubject.next([...currentToasts, newToast]);        // Auto-remove toast after duration
        if (newToast.duration && newToast.duration > 0) {
            setTimeout(() => {
                this.removeToast(newToast.id);
            }, newToast.duration);
        }
    }

    success(title: string, message?: string, duration?: number): void {
        this.addToast({
            type: 'success',
            title,
            message,
            duration
        });
    }

    error(title: string, message?: string, duration?: number): void {
        this.addToast({
            type: 'error',
            title,
            message,
            duration: duration ?? 7000 // Errores se muestran más tiempo
        });
    }

    warning(title: string, message?: string, duration?: number): void {
        this.addToast({
            type: 'warning',
            title,
            message,
            duration
        });
    }

    info(title: string, message?: string, duration?: number): void {
        this.addToast({
            type: 'info',
            title,
            message,
            duration
        });
    }

    removeToast(id: string): void {
        const currentToasts = this.toastsSubject.value;
        this.toastsSubject.next(currentToasts.filter(toast => toast.id !== id));
    }

    clearAll(): void {
        this.toastsSubject.next([]);
    }
}

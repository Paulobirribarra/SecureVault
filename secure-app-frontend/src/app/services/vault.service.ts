import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { CreateVaultFolderRequest, CreateVaultItemRequest, VaultFolder, VaultItem } from '../models/vault.model';

@Injectable({
    providedIn: 'root'
})
export class VaultService {
    private apiUrl = 'http://localhost:8000/api/vault';
    private vaultItemsSubject = new BehaviorSubject<VaultItem[]>([]);
    private vaultFoldersSubject = new BehaviorSubject<VaultFolder[]>([]);

    public vaultItems$ = this.vaultItemsSubject.asObservable();
    public vaultFolders$ = this.vaultFoldersSubject.asObservable();

    constructor(private http: HttpClient) {
        this.loadVaultData();
    }

    private getAuthHeaders(): HttpHeaders {
        const token = localStorage.getItem('access_token');
        return new HttpHeaders({
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        });
    }

    // Vault Items
    getVaultItems(): Observable<VaultItem[]> {
        return this.http.get<VaultItem[]>(`${this.apiUrl}/items/`, {
            headers: this.getAuthHeaders()
        });
    }

    getVaultItem(id: number): Observable<VaultItem> {
        return this.http.get<VaultItem>(`${this.apiUrl}/items/${id}/`, {
            headers: this.getAuthHeaders()
        });
    }

    createVaultItem(item: CreateVaultItemRequest): Observable<VaultItem> {
        return this.http.post<VaultItem>(`${this.apiUrl}/items/`, item, {
            headers: this.getAuthHeaders()
        });
    }

    updateVaultItem(id: number, item: Partial<VaultItem>): Observable<VaultItem> {
        return this.http.patch<VaultItem>(`${this.apiUrl}/items/${id}/`, item, {
            headers: this.getAuthHeaders()
        });
    }

    deleteVaultItem(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/items/${id}/`, {
            headers: this.getAuthHeaders()
        });
    }

    // Vault Folders
    getVaultFolders(): Observable<VaultFolder[]> {
        return this.http.get<VaultFolder[]>(`${this.apiUrl}/folders/`, {
            headers: this.getAuthHeaders()
        });
    }

    createVaultFolder(folder: CreateVaultFolderRequest): Observable<VaultFolder> {
        return this.http.post<VaultFolder>(`${this.apiUrl}/folders/`, folder, {
            headers: this.getAuthHeaders()
        });
    }

    updateVaultFolder(id: number, folder: Partial<VaultFolder>): Observable<VaultFolder> {
        return this.http.patch<VaultFolder>(`${this.apiUrl}/folders/${id}/`, folder, {
            headers: this.getAuthHeaders()
        });
    }

    deleteVaultFolder(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/folders/${id}/`, {
            headers: this.getAuthHeaders()
        });
    }

    // Utility methods
    loadVaultData(): void {
        this.getVaultItems().subscribe({
            next: (items) => this.vaultItemsSubject.next(items),
            error: (error) => console.error('Error loading vault items:', error)
        });

        this.getVaultFolders().subscribe({
            next: (folders) => this.vaultFoldersSubject.next(folders),
            error: (error) => console.error('Error loading vault folders:', error)
        });
    }

    refreshVaultData(): void {
        this.loadVaultData();
    }

    // Password generator
    generatePassword(length: number = 16, includeSpecial: boolean = true): string {
        const lowercase = 'abcdefghijklmnopqrstuvwxyz';
        const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const numbers = '0123456789';
        const special = '!@#$%^&*()_+-=[]{}|;:,.<>?';

        let charset = lowercase + uppercase + numbers;
        if (includeSpecial) {
            charset += special;
        }

        let password = '';

        // Asegurar al menos un carácter de cada tipo
        password += lowercase[Math.floor(Math.random() * lowercase.length)];
        password += uppercase[Math.floor(Math.random() * uppercase.length)];
        password += numbers[Math.floor(Math.random() * numbers.length)];

        if (includeSpecial) {
            password += special[Math.floor(Math.random() * special.length)];
        }

        // Llenar el resto de la longitud
        for (let i = password.length; i < length; i++) {
            password += charset[Math.floor(Math.random() * charset.length)];
        }

        // Mezclar los caracteres
        return password.split('').sort(() => Math.random() - 0.5).join('');
    }

    // Análisis de fortaleza de contraseña
    analyzePasswordStrength(password: string): {
        score: number;
        feedback: string[];
        strength: 'weak' | 'fair' | 'good' | 'strong';
    } {
        let score = 0;
        const feedback: string[] = [];

        // Longitud
        if (password.length >= 8) score += 1;
        else feedback.push('Use al menos 8 caracteres');

        if (password.length >= 12) score += 1;
        if (password.length >= 16) score += 1;

        // Complejidad
        if (/[a-z]/.test(password)) score += 1;
        else feedback.push('Incluya letras minúsculas');

        if (/[A-Z]/.test(password)) score += 1;
        else feedback.push('Incluya letras mayúsculas');

        if (/[0-9]/.test(password)) score += 1;
        else feedback.push('Incluya números');

        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        else feedback.push('Incluya símbolos especiales');

        // Patrones comunes
        if (!/(.)\1{2,}/.test(password)) score += 1;
        else feedback.push('Evite repetir caracteres');

        if (!/123|abc|qwe/i.test(password)) score += 1;
        else feedback.push('Evite secuencias comunes');

        let strength: 'weak' | 'fair' | 'good' | 'strong';
        if (score <= 3) strength = 'weak';
        else if (score <= 5) strength = 'fair';
        else if (score <= 7) strength = 'good';
        else strength = 'strong';

        return { score, feedback, strength };
    }
}

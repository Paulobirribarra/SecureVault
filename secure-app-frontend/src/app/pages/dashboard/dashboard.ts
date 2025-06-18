import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { User } from '../../models/user.model';
import { VaultFolder, VaultItem } from '../../models/vault.model';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { VaultService } from '../../services/vault.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  currentUser: User | null = null;
  vaultItems: VaultItem[] = [];
  vaultFolders: VaultFolder[] = [];
  recentItems: VaultItem[] = [];
  stats = {
    totalItems: 0,
    weakPasswords: 0,
    duplicatePasswords: 0,
    lastSync: new Date()
  }; constructor(
    private authService: AuthService,
    private vaultService: VaultService,
    private notificationService: NotificationService,
    private router: Router
  ) { } ngOnInit(): void {
    this.loadUserData();
    this.loadVaultData();
  }

  private loadUserData(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  private loadVaultData(): void {
    this.vaultService.vaultItems$.subscribe(items => {
      this.vaultItems = items;
      this.recentItems = items
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, 5);
      this.updateStats();
    });

    this.vaultService.vaultFolders$.subscribe(folders => {
      this.vaultFolders = folders;
    });
  }

  private updateStats(): void {
    this.stats.totalItems = this.vaultItems.length;    // Simulación de análisis de contraseñas débiles y duplicadas
    // En una implementación real, esto se haría en el backend
    this.stats.weakPasswords = this.vaultItems.filter(item =>
      item.item_type === 'login' && this.isWeakPassword(item.name)
    ).length;

    this.stats.duplicatePasswords = this.findDuplicatePasswords();
    this.stats.lastSync = new Date();
  }

  private isWeakPassword(password: string): boolean {
    // Simulación simple de detección de contraseñas débiles
    return password.length < 8 || !/[A-Z]/.test(password) || !/[0-9]/.test(password);
  }

  private findDuplicatePasswords(): number {
    // Simulación de detección de contraseñas duplicadas
    const passwords = this.vaultItems
      .filter(item => item.item_type === 'login')
      .map(item => item.name); // En realidad sería item.password después de descifrar

    const duplicates = passwords.filter((password, index) =>
      passwords.indexOf(password) !== index
    );

    return new Set(duplicates).size;
  }
  logout(): void {
    this.authService.logout().subscribe({
      next: () => {
        this.notificationService.success('Sesión cerrada', 'Has cerrado sesión correctamente');
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        // Incluso si hay error en el backend, limpiar sesión local y redirigir
        this.notificationService.success('Sesión cerrada', 'Has cerrado sesión correctamente');
        this.router.navigate(['/auth/login']);
      }
    });
  }
  getItemTypeIcon(item_type: string): string {
    switch (item_type) {
      case 'login': return 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z';
      case 'note': return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z';
      case 'card': return 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z';
      default: return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z';
    }
  }

  getItemTypeColor(item_type: string): string {
    switch (item_type) {
      case 'login': return 'text-blue-600';
      case 'note': return 'text-green-600';
      case 'card': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
}

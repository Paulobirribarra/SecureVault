import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
  selector: 'app-register',
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.html',
  styleUrl: './register.scss'
})
export class Register implements OnInit {
  registerForm!: FormGroup;
  isLoading = false;
  showPassword = false;
  showConfirmPassword = false;
  passwordStrength = {
    score: 0,
    feedback: [] as string[],
    strength: 'weak' as 'weak' | 'fair' | 'good' | 'strong'
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private notificationService: NotificationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.initForm();
  }

  private initForm(): void {
    this.registerForm = this.fb.group({
      firstName: ['', [Validators.required, Validators.minLength(2)]],
      lastName: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, this.passwordValidator]],
      confirmPassword: ['', [Validators.required]],
      acceptTerms: [false, [Validators.requiredTrue]]
    }, {
      validators: this.passwordMatchValidator
    });

    // Escuchar cambios en la contraseña para evaluar fortaleza
    this.registerForm.get('password')?.valueChanges.subscribe(password => {
      if (password) {
        this.passwordStrength = this.analyzePasswordStrength(password);
      }
    });
  }

  private passwordValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.value;
    if (!password) return null;

    const errors: ValidationErrors = {};

    if (password.length < 8) {
      errors['minLength'] = true;
    }

    if (!/[A-Z]/.test(password)) {
      errors['uppercase'] = true;
    }

    if (!/[a-z]/.test(password)) {
      errors['lowercase'] = true;
    }

    if (!/[0-9]/.test(password)) {
      errors['number'] = true;
    }

    if (!/[^A-Za-z0-9]/.test(password)) {
      errors['symbol'] = true;
    }

    return Object.keys(errors).length ? errors : null;
  }

  private passwordMatchValidator(form: AbstractControl): ValidationErrors | null {
    const password = form.get('password')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;

    if (password && confirmPassword && password !== confirmPassword) {
      return { passwordMismatch: true };
    }

    return null;
  }

  private analyzePasswordStrength(password: string): {
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

  onSubmit(): void {
    if (this.registerForm.valid && !this.isLoading) {
      this.isLoading = true;
      const formData = this.registerForm.value;

      this.authService.register(formData).subscribe({
        next: (response) => {
          this.notificationService.success(
            '¡Cuenta creada!',
            'Te hemos enviado un correo de verificación'
          );
          this.router.navigate(['/auth/login']);
        },
        error: (error) => {
          console.error('Error en registro:', error);
          let errorMessage = 'Error al crear la cuenta';

          if (error.status === 400) {
            if (error.error?.email) {
              errorMessage = 'El correo ya está registrado';
            } else if (error.error?.password) {
              errorMessage = 'La contraseña no cumple los requisitos';
            } else {
              errorMessage = 'Datos inválidos';
            }
          }

          this.notificationService.error('Error de registro', errorMessage);
          this.isLoading = false;
        },
        complete: () => {
          this.isLoading = false;
        }
      });
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  getPasswordStrengthColor(): string {
    switch (this.passwordStrength.strength) {
      case 'weak': return 'bg-red-500';
      case 'fair': return 'bg-yellow-500';
      case 'good': return 'bg-blue-500';
      case 'strong': return 'bg-green-500';
      default: return 'bg-gray-300';
    }
  }

  getPasswordStrengthText(): string {
    switch (this.passwordStrength.strength) {
      case 'weak': return 'Débil';
      case 'fair': return 'Regular';
      case 'good': return 'Buena';
      case 'strong': return 'Fuerte';
      default: return '';
    }
  }

  get firstName() { return this.registerForm.get('firstName'); }
  get lastName() { return this.registerForm.get('lastName'); }
  get email() { return this.registerForm.get('email'); }
  get password() { return this.registerForm.get('password'); }
  get confirmPassword() { return this.registerForm.get('confirmPassword'); }
  get acceptTerms() { return this.registerForm.get('acceptTerms'); }
}

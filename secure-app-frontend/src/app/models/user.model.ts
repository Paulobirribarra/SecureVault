// Modelos para el sistema de autenticación y usuarios

export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    short_name: string;
    is_active: boolean;
    email_verified: boolean;
    is_social_account: boolean;
    social_provider?: string;
    date_joined: string;
    last_login?: string;
    failed_login_attempts: number;
    is_account_locked: boolean;
}

export interface UserProfile {
    user: User;
    phone_number?: string;
    birth_date?: string;
    avatar?: string;
    age?: number;
    is_profile_public: boolean;
    two_factor_enabled: boolean;
    created_at: string;
    updated_at: string;
}

export interface UserSession {
    id: string;
    session_key: string;
    ip_address: string;
    user_agent: string;
    location_display?: string;
    device_info: string;
    created_at: string;
    last_activity: string;
    expires_at: string;
    is_active: boolean;
    is_current: boolean;
    is_expired: boolean;
}

export interface LoginRequest {
    email: string;
    password: string;
    remember_me?: boolean;
    totp_code?: string;
}

export interface LoginResponse {
    access: string;
    refresh: string;
    user: User;
    expires_in: number;
}

export interface RegisterRequest {
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
    terms_accepted: boolean;
}

export interface RegisterResponse {
    message: string;
    user_id: string;
    email: string;
}

export interface PasswordChangeRequest {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
}

export interface ApiError {
    error: string;
    details?: any;
}

export interface ApiResponse<T = any> {
    data?: T;
    message?: string;
    error?: string;
}

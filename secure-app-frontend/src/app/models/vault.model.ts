// Modelos para el sistema de baúl de contraseñas

export interface VaultFolder {
    id: string;
    name: string;
    color: string;
    created_at: string;
    updated_at: string;
}

export interface VaultItem {
    id: string;
    name: string;
    item_type: 'login' | 'note' | 'card' | 'identity';
    type_display: string;
    is_favorite: boolean;
    folder?: string;
    created_at: string;
    updated_at: string;
    last_accessed?: string;
    access_count: number;
}

export interface VaultItemDetail extends VaultItem {
    data: VaultItemData;
}

export interface VaultItemData {
    // Para tipo 'login'
    username?: string;
    password?: string;
    url?: string;
    totp?: string;
    notes?: string;

    // Para tipo 'note'
    content?: string;

    // Para tipo 'card'
    card_holder?: string;
    card_number?: string;
    expiry_month?: string;
    expiry_year?: string;
    cvv?: string;

    // Para tipo 'identity'
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    address?: string;
}

export interface CreateVaultItemRequest {
    name: string;
    item_type: 'login' | 'note' | 'card' | 'identity';
    folder_id?: string;
    is_favorite?: boolean;
    data: VaultItemData;
    master_password: string;
}

export interface CreateVaultFolderRequest {
    name: string;
    color: string;
}

export interface UpdateVaultItemRequest {
    name?: string;
    folder_id?: string;
    is_favorite?: boolean;
    data?: Partial<VaultItemData>;
    master_password: string;
}

export interface VaultItemShare {
    id: string;
    vault_item: VaultItem;
    shared_by: string;
    shared_with: string;
    permission: 'read' | 'write';
    created_at: string;
    expires_at?: string;
    is_active: boolean;
}

export interface VaultActivity {
    id: string;
    action: 'create' | 'read' | 'update' | 'delete' | 'share' | 'unshare' | 'export' | 'import';
    description: string;
    vault_item?: VaultItem;
    ip_address?: string;
    user_agent?: string;
    timestamp: string;
}

export interface MasterPasswordRequest {
    password: string;
}

export interface MasterPasswordChangeRequest {
    current_password: string;
    new_password: string;
    new_password_confirm: string;
}

export interface UnlockVaultRequest {
    master_password: string;
}

export interface VaultStatus {
    is_unlocked: boolean;
    has_master_password: boolean;
    items_count: number;
    last_unlock?: string;
    session_expires?: string;
}

export interface PasswordGeneratorOptions {
    length: number;
    include_uppercase: boolean;
    include_lowercase: boolean;
    include_numbers: boolean;
    include_symbols: boolean;
    exclude_ambiguous: boolean;
}

export interface GeneratedPassword {
    password: string;
    strength: 'weak' | 'fair' | 'good' | 'strong';
    entropy: number;
}

export interface SecurityAnalysis {
    total_items: number;
    weak_passwords: number;
    duplicate_passwords: number;
    old_passwords: number;
    compromised_passwords: number;
    security_score: number;
    recommendations: string[];
}

export interface ExportVaultRequest {
    format: 'json' | 'csv';
    master_password: string;
    include_folders?: boolean;
    folder_ids?: string[];
}

export interface ImportVaultRequest {
    format: 'json' | 'csv' | 'bitwarden' | 'chrome' | 'firefox';
    file_data: string;
    master_password: string;
    create_folders?: boolean;
}

# ====================================================================
# SecureVault - Configuración de Base de Datos
# ====================================================================
# Este script configura la base de datos PostgreSQL y ejecuta migraciones
# Ejecutar desde la raíz del proyecto: .\scripts\setup_database.ps1

Write-Host "🗄️ SecureVault - Configuración de Base de Datos" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecutar desde la raíz del proyecto SecureVault" -ForegroundColor Red
    exit 1
}

# Cambiar al directorio backend
Set-Location "backend"

# Activar entorno virtual
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Error: Entorno virtual no encontrado. Ejecutar setup_project.ps1 primero" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Verificar archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: Archivo .env no encontrado. Ejecutar setup_project.ps1 primero" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "🔧 Verificando conexión a PostgreSQL..." -ForegroundColor Yellow

# Intentar crear la base de datos (opcional, puede fallar si ya existe)
Write-Host "🗄️ Creando base de datos..." -ForegroundColor Yellow
$createDb = Read-Host "¿Crear base de datos 'secure_app_db'? (y/N)"
if ($createDb -eq "y" -or $createDb -eq "Y") {
    try {
        $password = Read-Host "Contraseña de PostgreSQL (usuario postgres)" -AsSecureString
        $plaintextPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
        
        # Crear base de datos usando psql
        $env:PGPASSWORD = $plaintextPassword
        psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE secure_app_db;" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Base de datos creada exitosamente" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Base de datos ya existe o error en creación" -ForegroundColor Yellow
        }
        
        # Limpiar variable de entorno
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    } catch {
        Write-Host "⚠️  No se pudo crear la base de datos automáticamente" -ForegroundColor Yellow
        Write-Host "   Crear manualmente: CREATE DATABASE secure_app_db;" -ForegroundColor Gray
    }
}

Write-Host "🔧 Creando migraciones..." -ForegroundColor Yellow

# Crear migraciones para usuarios primero
try {
    python manage.py makemigrations usuarios
    Write-Host "✅ Migraciones de usuarios creadas" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creando migraciones de usuarios" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Crear migraciones para core
try {
    python manage.py makemigrations core
    Write-Host "✅ Migraciones de core creadas" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creando migraciones de core" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "🔧 Aplicando migraciones..." -ForegroundColor Yellow

# Aplicar todas las migraciones
try {
    python manage.py migrate
    Write-Host "✅ Migraciones aplicadas exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error aplicando migraciones" -ForegroundColor Red
    Write-Host "   Verificar configuración de base de datos en .env" -ForegroundColor Gray
    Set-Location ".."
    exit 1
}

# Preguntar si crear superusuario
$createSuperuser = Read-Host "¿Crear superusuario para admin? (y/N)"
if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
    Write-Host "🔧 Creando superusuario..." -ForegroundColor Yellow
    python manage.py createsuperuser
}

# Volver a la raíz
Set-Location ".."

Write-Host ""
Write-Host "🎉 Base de datos configurada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximo paso:" -ForegroundColor Cyan
Write-Host "   Ejecutar: .\scripts\run_servers.ps1" -ForegroundColor White
Write-Host ""

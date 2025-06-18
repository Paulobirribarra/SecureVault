# ====================================================================
# SecureVault - Script de Limpieza
# ====================================================================
# Este script limpia archivos temporales, caché y resetea el proyecto
# Ejecutar desde la raíz del proyecto: .\scripts\clean_project.ps1

param(
    [switch]$Full,
    [switch]$Cache,
    [switch]$Database
)

Write-Host "🧹 SecureVault - Limpieza de Proyecto" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

if (-not $Full -and -not $Cache -and -not $Database) {
    Write-Host "Uso del script:" -ForegroundColor Yellow
    Write-Host "  .\scripts\clean_project.ps1 -Cache     # Limpiar solo caché" -ForegroundColor White
    Write-Host "  .\scripts\clean_project.ps1 -Database  # Resetear base de datos" -ForegroundColor White
    Write-Host "  .\scripts\clean_project.ps1 -Full      # Limpieza completa" -ForegroundColor White
    exit 0
}

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "backend") -or -not (Test-Path "secure-app-frontend")) {
    Write-Host "❌ Error: Ejecutar desde la raíz del proyecto SecureVault" -ForegroundColor Red
    exit 1
}

if ($Cache -or $Full) {
    Write-Host "🧹 Limpiando archivos de caché..." -ForegroundColor Yellow
    
    # Limpiar caché de Python
    Get-ChildItem -Path "." -Recurse -Name "__pycache__" -Directory | ForEach-Object {
        Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Eliminado: $_" -ForegroundColor Gray
    }
    
    # Limpiar archivos .pyc
    Get-ChildItem -Path "." -Recurse -Name "*.pyc" | ForEach-Object {
        Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue
        Write-Host "   Eliminado: $_" -ForegroundColor Gray
    }
    
    # Limpiar node_modules (si se especifica limpieza completa)
    if ($Full -and (Test-Path "secure-app-frontend\node_modules")) {
        Write-Host "🧹 Eliminando node_modules..." -ForegroundColor Yellow
        Remove-Item -Path "secure-app-frontend\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ Caché limpiado" -ForegroundColor Green
}

if ($Database -or $Full) {
    Write-Host "🗄️ Reseteando base de datos..." -ForegroundColor Yellow
    
    $confirm = Read-Host "⚠️  Esto eliminará TODOS los datos. ¿Continuar? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        
        # Eliminar migraciones
        Write-Host "🧹 Eliminando migraciones..." -ForegroundColor Yellow
        Remove-Item -Path "backend\core\migrations\*.py" -Exclude "__init__.py" -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "backend\usuarios\migrations\*.py" -Exclude "__init__.py" -Force -ErrorAction SilentlyContinue
        
        # Eliminar base de datos SQLite si existe
        if (Test-Path "backend\db.sqlite3") {
            Remove-Item -Path "backend\db.sqlite3" -Force
            Write-Host "   Eliminado: db.sqlite3" -ForegroundColor Gray
        }
        
        Write-Host "✅ Base de datos reseteada" -ForegroundColor Green
        Write-Host "📋 Ejecutar setup_database.ps1 para reconfigurar" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

if ($Full) {
    Write-Host "🧹 Limpieza completa..." -ForegroundColor Yellow
    
    # Eliminar entorno virtual
    if (Test-Path "backend\venv") {
        Write-Host "🧹 Eliminando entorno virtual..." -ForegroundColor Yellow
        Remove-Item -Path "backend\venv" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Eliminar archivo .env (mantener .env.example)
    if (Test-Path "backend\.env") {
        $confirmEnv = Read-Host "¿Eliminar archivo .env con configuraciones? (y/N)"
        if ($confirmEnv -eq "y" -or $confirmEnv -eq "Y") {
            Remove-Item -Path "backend\.env" -Force
            Write-Host "   Eliminado: .env" -ForegroundColor Gray
        }
    }
    
    Write-Host "✅ Limpieza completa terminada" -ForegroundColor Green
    Write-Host "📋 Ejecutar setup_project.ps1 para reconfigurar todo" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 Limpieza completada!" -ForegroundColor Green
Write-Host ""

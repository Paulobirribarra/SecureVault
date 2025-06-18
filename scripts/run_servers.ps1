# ====================================================================
# SecureVault - Ejecutar Servidores de Desarrollo
# ====================================================================
# Este script inicia ambos servidores (backend y frontend) simultaneamente
# Ejecutar desde la raíz del proyecto: .\scripts\run_servers.ps1

Write-Host "🚀 SecureVault - Iniciando Servidores" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "backend") -or -not (Test-Path "secure-app-frontend")) {
    Write-Host "❌ Error: Ejecutar desde la raíz del proyecto SecureVault" -ForegroundColor Red
    exit 1
}

Write-Host "🐍 Iniciando Backend (Django)..." -ForegroundColor Yellow

# Iniciar backend en una nueva ventana de PowerShell
$backendScript = @"
# Configurar política de ejecución para evitar errores (si está disponible)
try {
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force -ErrorAction SilentlyContinue
} catch {
    # Ignorar errores de Set-ExecutionPolicy en PowerShell Core
}

Set-Location (Join-Path `$projectRoot "backend")
Write-Host '🔧 Configurando entorno Python...' -ForegroundColor Yellow

# Usar Python específico del venv para evitar conflictos
`$projectRoot = Split-Path -Parent `$PSScriptRoot
`$pythonExe = Join-Path `$projectRoot "backend\venv\Scripts\python.exe"

Write-Host '🔍 Verificando Python del entorno virtual...' -ForegroundColor Yellow
if (Test-Path `$pythonExe) {
    & `$pythonExe -c \"import sys; print('Python activo:', sys.executable)\"
    Write-Host '✅ Entorno virtual configurado correctamente' -ForegroundColor Green
} else {
    Write-Host '❌ Error: Entorno virtual no encontrado' -ForegroundColor Red
    Write-Host 'Ejecutar: .\scripts\setup_project.ps1' -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host '🚀 Backend iniciado en http://localhost:8000' -ForegroundColor Green
Write-Host '📚 API Docs: http://localhost:8000/api/docs/' -ForegroundColor Cyan
Write-Host '⚙️ Admin: http://localhost:8000/admin/' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Presiona Ctrl+C para detener el servidor' -ForegroundColor Yellow

# Usar Python del entorno virtual directamente
& `$pythonExe manage.py runserver
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendScript

# Esperar un momento para que el backend inicie
Start-Sleep -Seconds 3

Write-Host "🅰️ Iniciando Frontend (Angular)..." -ForegroundColor Yellow

# Iniciar frontend en una nueva ventana de PowerShell
$frontendScript = @"
# Configurar política de ejecución para evitar errores (si está disponible)
try {
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force -ErrorAction SilentlyContinue
} catch {
    # Ignorar errores de Set-ExecutionPolicy en PowerShell Core
}

Set-Location (Join-Path `$projectRoot "secure-app-frontend")

Write-Host '🔧 Verificando directorio de trabajo...' -ForegroundColor Yellow
Write-Host "PWD: `$((Get-Location).Path)" -ForegroundColor Gray

Write-Host '📦 Verificando package.json...' -ForegroundColor Yellow
if (Test-Path 'package.json') {
    Write-Host '✅ package.json encontrado' -ForegroundColor Green
    
    # Verificar que node_modules existe
    if (-not (Test-Path 'node_modules')) {
        Write-Host '📦 Instalando dependencias npm...' -ForegroundColor Yellow
        npm install
    }
    
} else {
    Write-Host '❌ package.json NO encontrado' -ForegroundColor Red
    Write-Host 'Directorio actual:' -ForegroundColor Gray
    Get-ChildItem | Select-Object Name, PSIsContainer | Format-Table -AutoSize
    Read-Host 'Presiona Enter para continuar de todas formas...'
}

Write-Host '🚀 Frontend iniciado en http://localhost:4200' -ForegroundColor Green
Write-Host ''
Write-Host 'Presiona Ctrl+C para detener el servidor' -ForegroundColor Yellow

# Ejecutar npm con verificación de directorio
if (Test-Path 'package.json') {
    npm start
} else {
    Write-Host '❌ Error: No se puede iniciar npm sin package.json' -ForegroundColor Red
    Read-Host 'Presiona Enter para cerrar...'
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendScript

Write-Host ""
Write-Host "🎉 Servidores iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   Frontend:      http://localhost:4200" -ForegroundColor White
Write-Host "   Backend API:   http://localhost:8000/api" -ForegroundColor White
Write-Host "   Documentación: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host "   Admin Django:  http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "💡 Para detener: Cerrar las ventanas de PowerShell o presionar Ctrl+C" -ForegroundColor Gray
Write-Host ""
